from bs4 import BeautifulSoup as bs
import base64, struct, zlib

class Processor():
    instrument = ""
    spectrum_dict = dict()
    spectrum_list = []

    def run(self, content):
        print("AAA")
        self.spectrum_list = self.construct_spectrum_list(content)
        self.write_spectrum_list_to_file(self.spectrum_list)

    def construct_spectrum_list(self, content):
        print("BBB")
        spectrum_dict = dict()
        spectrum_list = []

        all_spectrum_list = list(bs(content, "xml").find_all("run")[0].find_all("spectrumList")[0].find_all("spectrum"))
        print("All spectra: ", len(all_spectrum_list))

        all_ms2_spectra = list(filter(lambda x: x.find_all("cvParam")[1].attrs["value"]=="2", all_spectrum_list))
        print("Starting length of MS2 spectra: ", len(all_ms2_spectra))

        all_ms2_spectra = [all_ms2_spectra[6]]

        '''all_spectrum_list[2833], all_spectrum_list[2895], all_spectrum_list[2920], all_spectrum_list[3021], all_spectrum_list[3500], '''
        
        i = 0
        for spectrum in all_ms2_spectra:
            #print("In the for loop")
            spectrum_mz_list = []
            spectrum_intensity_list = []
            spectrum_id = spectrum.attrs["id"]
            spectrum_children_ids = []
            spectrum_parent_id = ""
            rt = bs(str(spectrum), "xml").find_all("scanList")[0].find_all("scan")[0].find_all("cvParam")[0].attrs["value"]
            rt = rt if rt else bs(str(spectrum), "xml").find_all("scanList")[0].find_all("scan")[0].find_all("userParam")[0].attrs["value"]
            ms_level = bs(str(spectrum), "xml").find_all("cvParam")[1].attrs["value"]
            #print("MS Level, ", ms_level)
            if ms_level=="2":
                precursor_mz = bs(str(spectrum), "xml").find_all("precursorList")[0].find_all("selectedIonList")[0].find_all("selectedIon")[0].find_all("cvParam")[0].attrs["value"]
                precursor_charge = bs(str(spectrum), "xml").find_all("precursorList")[0].find_all("selectedIonList")[0].find_all("selectedIon")[0].find_all("cvParam")[1].attrs["value"]
                #print("Just before loop...")
                for binaryDataArray in bs(str(spectrum), "xml").find_all("binaryDataArrayList")[0].find_all("binaryDataArray"):
                    #print("Just inside loop...")
                    #print(binaryDataArray)
                    array_type = ""
                    encoded_data = ""
                    floating_point_type = ""
                    for cvParam in binaryDataArray.find_all(lambda x: x.name == "cvParam" and (x.attrs["name"] == "m/z array" or x.attrs["name"] == "intensity array")):
                        array_type = cvParam.attrs["name"]
                    for cvParam in binaryDataArray.find_all(lambda x: x.name == "cvParam" and (x.attrs["name"] == "64-bit float" or x.attrs["name"] == "32-bit float")):
                        floating_point_type = cvParam.attrs["name"]
                    for binaryData in binaryDataArray.find_all(lambda x: x.name=="binary"):
                        encoded_data = binaryData.text.encode()
                        if array_type == "m/z array" and floating_point_type:
                            if rt=="8.2546478":
                                print(f"m/z array: {encoded_data}")
                            spectrum_mz_list = self.decode_binary(encoded_data, floating_point_type)
                            #if not spectrum_mz_list==None:
                                #print(f"MZ: {spectrum_mz_list}")
                        elif array_type == "intensity array" and floating_point_type:
                            if rt=="8.2546478":
                                print(f"intensity array: {encoded_data}")
                            spectrum_intensity_list = self.decode_binary(encoded_data, floating_point_type)
                            #if not spectrum_intensity_list==None:
                                #print(f"Intensity: {spectrum_intensity_list}")
                if spectrum_intensity_list and spectrum_mz_list and len(spectrum_intensity_list)>0 and len(spectrum_mz_list)>0 and spectrum.find_all(lambda x: x.name=='cvParam' and x.attrs["name"]=="ms level")[0].attrs["value"] == "1":
                    new_spectrum = Spectrum(spectrum_mz_list, spectrum_intensity_list, rt, spectrum_id, precursor_mz, precursor_charge)
                    #spectrum_dict[spectrum.attrib["id"]] = new_spectrum
                    spectrum_list.append(new_spectrum)
                elif spectrum_intensity_list and spectrum_mz_list and len(spectrum_intensity_list)>0 and len(spectrum_mz_list)>0 and spectrum.find_all(lambda x: x.name=='cvParam' and x.attrs["name"]=="ms level")[0].attrs["value"] == "2":
                    new_spectrum = Spectrum(spectrum_mz_list, spectrum_intensity_list, rt, spectrum_id, precursor_mz, precursor_charge)
                    #for precursor in spectrum.find_all("precursorList")[0].find_all("precursor"):
                    #    new_spectrum.addPrecursor(spectrum_dict[precursor.attrs["spectrumRef"]])
                    spectrum_list.append(new_spectrum)
            i += 1
            print(f'On spectrum {i}')
        #print(spectrum_list)
        return spectrum_list

    def decode_binary(self, encoded_data, bits):
        raw_data = base64.decodebytes(encoded_data)
        raw_data = zlib.decompress(raw_data)
        try:
            output_data = struct.unpack(("<%s"+("d" if bits == "64-bit float" else "f")) % (len(raw_data)//(8 if bits == "64-bit float" else 4)), raw_data)
        except:
            return None
        return output_data

    def write_spectrum_list_to_file(self, spectrum_list):
        print("Length of MS2 spectra is: ", len(spectrum_list))
        #print(spectrum_list)
        spectrum_list_file = open("/usr/src/new_spectrum_list.txt", "x")
        i = 1
        for spectrum in spectrum_list:
            spectrum_list_file.write("Precursor\n")
            spectrum_list_file.write(spectrum.getPrecursorMZ()+","+spectrum.getPrecursorCharge()+"\n")
            spectrum_list_file.write("RT        Peak List\n")
            spectrum_list_file.write(str(spectrum.getRT())+"        ")
            for peak in spectrum.getPeakList():
                spectrum_list_file.write(str(peak.mz)+","+str(peak.intensity)+"     ")
            spectrum_list_file.write("\n")
            i += 1

class Spectrum():
    rt = 0.0
    peak_list = []
    spectrum_id = ""
    precursor_mz = 0.0
    precursor_charge = 0

    def __init__(self, spectrum_mz_list, spectrum_intensity_list, rt, spectrum_id, precursor_mz, precursor_charge):
        self.rt = rt
        self.precursor_mz = precursor_mz
        self.precursor_charge = precursor_charge
        self.peak_list = self.construct_peak_list(rt, spectrum_mz_list, spectrum_intensity_list)
        self.spectrum_id = spectrum_id

    def getPeakList(self):
        return self.peak_list

    def getRT(self):
        return self.rt

    def getPrecursorMZ(self):
        return self.precursor_mz

    def getPrecursorCharge(self):
        return self.precursor_charge

    def getSpectrumID(self):
        return self.spectrum_id

    def construct_peak_list(self, rt, spectrum_mz_list, spectrum_intensity_list):
        peak_list = []
        for mz in spectrum_mz_list:
            peak = Peak(rt, mz, spectrum_intensity_list[len(peak_list)])
            peak_list.append(peak)
        return peak_list

    def setRT(self, rt):
        self.rt = rt

class Peak():
    rt = 0.0
    mz = 0.0
    intensity = 0.0

    def __init__(self, rt, mz, intensity):
        self.rt = rt
        self.mz = mz
        self.intensity = intensity

'''if __name__ == "__main__":
    processor = Processor()
    f = open("C:\\Users\\Kassim Santone\\Desktop\\20190218_QExHFX2_RSLC4_PST_25ngHeLa_1ulloop_PepMap_1hr_60k_03.mzML", "r")
    processor.run(f.read())'''