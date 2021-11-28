import threading
import base64, struct, xml.etree.ElementTree as ET
import os.path
import json
from pathlib import Path
from bs4 import BeautifulSoup as bs
from django.core.files import File
from django.conf import settings
from queue import Queue

#from .DeNovo import run_denovo
from celery import shared_task
#from celery.task import Task
from celery_progress.backend import ProgressRecorder

#from algorithm_progresses.models import AlgorithmProgress
from time import sleep
#base_dir = settings.BASE_DIR

class CreatePipelineTasks(threading.Thread):
    title = ""
    algorithms = []
    inputs = []
    queue = Queue()
    def __init__(self, title, algorithms, inputs, queue):
        self.title = title
        self.algorithms = algorithms
        self.inputs = inputs
        self.queue = queue
        print("XYZ")
        threading.Thread.__init__(self)
        queue = self.queue
        print("Done")

    def run(self):
        try:
            print("In try.")
            #print("Sample data:\n")
            #print(self.inputs['sample_data'])
            #mzml_contents = b" ".join(self.inputs['sample_data'])
            #print("MzML contents initalized to:\n")
            #print(mzml_contents)
            #print("And with bs we get:\n")
            #print(bs(mzml_contents, "xml"))
            #mzml_contents = str(bs(mzml_contents, "xml").find_all("mzML")[0])
            #print("Right before processor.")
            #print(mzml_contents)
            print("Right before...")
            #execute_algorithm_and_update_progress.delay()
            #processor = Processor.delay(mzml_contents)
            processes = begin_pipeline_execution(self.title, self.algorithms, self.inputs)
            tasks = []
            print("After, after...")
            algorithms_to_task_ids = {}
            #algorithms_to_task_ids["Spectral"] = processor.task_id
            print("Why?")
            print(processes)
            for process in processes:
                task = run_pipeline.delay(process[0])
                algorithms_to_task_ids[process[0].split("\\")[-1]] = task.task_id
                self.queue.put(algorithms_to_task_ids)
            print("And how?")
        except Exception as e:
            print(e)

@shared_task(bind=True)
def execute_algorithm_and_update_progress(self):
    print("Inside")
    for i in range(10):
        print(i)
    return "Done"
    '''algorithm_progress = AlgorithmProgress.objects.create(pipeline="Discovery Omics", algorithm_number=1)
    for i in range(20):
        sleep(2)
        algorithm_progress.percent += 5
        print(algorithm_progress.percent)'''

'''@shared_task(bind=True)
def get_log_info(self):
    logging_file = os.path.join(base_dir, "logging.txt")
    print(os.path.join(base_dir, "logging.txt"))
    print(logging_file)
    num_lines = 0
    progress_recorder = ProgressRecorder(self)
    print(os.path.isfile(logging_file))
    while not os.path.isfile(logging_file):
        i = 5
        print(i)
    print(os.path.isfile(logging_file))
    while True:
        num_lines = sum(1 for line in open(logging_file, "r"))
        if num_lines==371:
            print("About to break!")
            break
        print("Num lines")
        print(num_lines)
        progress_recorder.set_progress(num_lines, 371, f'DeNovo sequencing')
    print("Out of while loop...")
    print(num_lines)'''

def begin_pipeline_execution(title, algorithms, inputs):
    processes = []
    spectral = True
    print(algorithms)
    for algorithm in algorithms.split(","):
        add_algorithm_to_file(algorithm, processes)
    print("Done!")
    return processes

def add_algorithm_to_file(algorithm, processes):
    print("Just in...")
    algorithm_to_executable = {"DeNovo": "DeNovoSequencingAlgorithm.exe", "Database": "DatabaseSearchAlgorithm.exe", "FDR": "FDR.exe"}
    print("Huh?")
    print(algorithm_to_executable)
    algorithm_reqs = [settings.STATICFILES_DIRS[0]+"\\algorithms\\"+algorithm_to_executable[algorithm]]
    print("Adding algorithms.")
    if algorithm=="DeNovo":
        processes.append([algorithm_reqs[0]])#, os.path.join(base_dir, "spectrum_list_29.txt")])
    else:
        processes.append([algorithm_reqs[0]])

@shared_task(bind=True)
def run_pipeline(self, process):
    print("Inside")
    progress_recorder = ProgressRecorder(self)
    for i in range(10):
        sleep(10)
        progress_recorder.set_progress(i+1, 10, f'On iteration {i}.')
        print(i)
    return "Done"
    '''print(process)
    if len(process)==2:
        print("In the pipeline run...")
        run_denovo.run_denovo_func()
    return 'Done'

class Processor(Task):
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
        print("CCC")

        progress_recorder = ProgressRecorder(self)

        print("DDD")
        i, count = 0, len(all_spectrum_list)
        for spectrum in all_spectrum_list:
            print("In the for loop")
            spectrum_mz_list = []
            spectrum_intensity_list = []
            spectrum_id = spectrum.attrs["id"]
            spectrum_children_ids = []
            spectrum_parent_id = ""
            rt = bs(str(spectrum), "xml").find_all("scanList")[0].find_all("scan")[0].find_all("cvParam")[0].attrs["value"]
            rt = rt if rt else bs(str(spectrum), "xml").find_all("scanList")[0].find_all("scan")[0].find_all("userParam")[0].attrs["value"]
            for binaryDataArray in bs(str(spectrum), "xml").find_all("binaryDataArrayList")[0].find_all("binaryDataArray"):
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
                        spectrum_mz_list = self.decode_binary(encoded_data, floating_point_type)
                    elif array_type == "intensity array" and floating_point_type:
                        spectrum_intensity_list = self.decode_binary(encoded_data, floating_point_type)
            if spectrum_intensity_list and spectrum_mz_list and len(spectrum_intensity_list)>0 and len(spectrum_mz_list)>0 and spectrum.find_all(lambda x: x.name=='cvParam' and x.attrs["name"]=="ms level")[0].attrs["value"] == "1":
                new_spectrum = Spectrum(spectrum_mz_list, spectrum_intensity_list, rt, spectrum_id)
                #spectrum_dict[spectrum.attrib["id"]] = new_spectrum
                spectrum_list.append(new_spectrum)
            elif spectrum_intensity_list and spectrum_mz_list and len(spectrum_intensity_list)>0 and len(spectrum_mz_list)>0 and spectrum.find_all(lambda x: x.name=='cvParam' and x.attrs["name"]=="ms level")[0].attrs["value"] == "2":
                new_spectrum = Spectrum(spectrum_mz_list, spectrum_intensity_list, rt, spectrum_id)
                #for precursor in spectrum.find_all("precursorList")[0].find_all("precursor"):
                #    new_spectrum.addPrecursor(spectrum_dict[precursor.attrs["spectrumRef"]])
                spectrum_list.append(new_spectrum)
            i += 1
            progress_recorder.set_progress(i, count, f'On spectrum {i}')
        return spectrum_list

    def decode_binary(self, encoded_data, bits):
        raw_data = base64.decodebytes(encoded_data)
        try:
            output_data = struct.unpack(("<%s"+("d" if bits == "64-bit float" else "f")) % (len(raw_data)//(8 if bits == "64-bit float" else 4)), raw_data)
        except:
            return None
        return output_data

    def write_spectrum_list_to_file(self, spectrum_list):
        spectrum_list_file = open(
            os.path.join(base_dir, "spectrum_list_29.txt"), "x")
        spectrum_list_file.write("RT        Peak List\n")
        for spectrum in spectrum_list:
            spectrum_list_file.write(str(spectrum.getRT())+"        ")
            for peak in spectrum.getPeakList():
                spectrum_list_file.write(str(peak.mz)+","+str(peak.intensity)+"     ")
            spectrum_list_file.write("\n")

class Spectrum():
    rt = 0.0
    peak_list = []
    spectrum_id = ""

    def __init__(self, spectrum_mz_list, spectrum_intensity_list, rt, spectrum_id):
        self.rt = rt
        self.peak_list = self.construct_peak_list(rt, spectrum_mz_list, spectrum_intensity_list)
        self.spectrum_id = spectrum_id

    def getPeakList(self):
        return self.peak_list

    def getRT(self):
        return self.rt

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
        self.intensity = intensity'''