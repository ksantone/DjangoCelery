# Django-related imports
from django.shortcuts import render
from .models import Pipeline
#from .tasks import sleeping
from queue import Queue

# Processor-related imports
import base64, struct, xml.etree.ElementTree as ET
import os.path
import subprocess
import json
from pathlib import Path
#from bs4 import BeautifulSoup as bs
from django.core.files import File
from django.conf import settings
from .thread import CreatePipelineTasks
from django.http import JsonResponse
from django.views.generic import View

#global queue

# Create your views here.
def pipeline_list_view(request):
    queryset = Pipeline.objects.all() # List of pipelines
    context = {
        "object_list": queryset
    }
    return render(request, "pipelines/pipeline_list.html", context)

def pipeline_detail_view(request, id):
    obj = Pipeline.objects.get(id=id)
    input_files = {}
    if request.method == "POST":
        input_files['sample_data'] = request.FILES["SampleDataFile"]
    context = {
        "object": obj,
        "inputs": obj.inputs.split("|"),
        "input_files": input_files
    }
    print("And now...")
    print(context)
    return render(request, "pipelines/pipeline_detail.html", context)

def pipeline_execute_view(request, id):
    print("In execution")
    print(request)
    print(request.FILES)
    print("And the pipeline is...")
    context = {}
    obj = Pipeline.objects.get(id=id)
    print(obj)
    context["object"] = obj
    inputs = {}
    execution_map = {}
    queue = Queue()
    print("Is it in?")
    if request.method == "POST":
        context['pipeline_title'] = obj.title
        inputs['sample_data'] = request.FILES["SampleDataFile"]
        print(inputs['sample_data'])
        inputs['spec_lib'] = request.POST.get("SpecLibFile", None)
        inputs['iRTs'] = request.POST.get("iRTsFile", None)
        context["sample_data"] = inputs['sample_data']
        context["spec_lib"] = inputs['spec_lib']
        context["iRTs"] = inputs['iRTs']
        context["algorithms"] = obj.algorithms.split(",")
        tasks = []
        algorithms_to_task_ids = {}
        print("About to create pipeline tasks...")
        print(obj)
        print(obj.algorithms)
        CreatePipelineTasks(obj.title, obj.algorithms, inputs, queue).start()
        print("Done creating pipeline tasks...")
        print(queue)
        algorithm_size = len(obj.algorithms.split(","))
        while True:
            flag = not (queue.qsize() == algorithm_size)
            if flag:
                pass
            else:
                print("In else statement")
                algorithm_to_executable = {"DeNovo": "DeNovoSequencingAlgorithm.exe", "Database": "DatabaseSearchAlgorithm.exe"}#, "FDR": "FDR.exe"}
                algorithms_to_task_ids = queue.get()
                print(algorithms_to_task_ids)
                print(context["algorithms"])
                for algorithm in context["algorithms"]:
                    context['task_id_'+algorithm] = algorithms_to_task_ids[algorithm_to_executable[algorithm]]
                break
        count = 0
    print(algorithms_to_task_ids)
    print(context)
    return render(request, "pipelines/pipeline_execute.html", context)

def create_execution_map(algorithms):
    new_map = {}
    current_val = list(algorithms)[0]
    new_map[current_val] = "Waiting..."
    if isinstance(algorithms[current_val], str):
        temp_map = new_map.update({algorithms[current_val]: "Waiting..."})
    else:
        new_map.update(create_execution_map(algorithms[current_val]))
    return new_map