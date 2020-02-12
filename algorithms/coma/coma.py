import subprocess
import time
import os

from algorithms.base_matcher import BaseMatcher
from data_loader.base_loader import BaseLoader
from utils.utils import get_project_root, get_table_from_dataset_path


class Coma(BaseMatcher):

    def __init__(self, max_n: int, strategy: str):
        self.max_n = max_n
        self.strategy = strategy

    def get_matches(self, source_data_loader: BaseLoader, target_data_loader: BaseLoader, dataset_name: str):

        coma_output_path = get_project_root() + "/algorithms/coma/coma_output/output.txt"

        self.run_coma_jar(source_data_loader, target_data_loader, coma_output_path)

        raw_output = self.read_coma_output(coma_output_path)

        os.remove(coma_output_path)

        return self.process_coma_output(raw_output, source_data_loader.data_path, target_data_loader.data_path)

    def run_coma_jar(self, source_data_loader, target_data_loader, coma_output_path):
        jar_path = get_project_root() + "/algorithms/coma/artifact/coma.jar"

        run_jar_command = "java -cp " + jar_path + " -DinputFile1=" + source_data_loader.data_path \
                          + " -DinputFile2=" + target_data_loader.data_path + \
                          " -DoutputFile=" + coma_output_path + " -DmaxN=" \
                          + str(self.max_n) + " -Dstrategy=" + self.strategy + " Main"

        proc = subprocess.Popen(run_jar_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        time.sleep(1)
        proc.terminate()
        proc.communicate()

    @staticmethod
    def read_coma_output(coma_output_path):
        with open(coma_output_path) as f:
            matches = f.readlines()
        matches = [x.strip() for x in matches]
        matches.pop()
        return matches

    @staticmethod
    def process_coma_output(matches, dataset1, dataset2):
        formatted_output = dict()
        table1 = get_table_from_dataset_path(dataset1)
        table2 = get_table_from_dataset_path(dataset2)
        for match in matches:
            m, similarity = match.split(":")
            m1, m2 = m.split(" <-> ")
            _, column1 = m1.split(".")
            _, column2 = m2.split(".")
            formatted_output[((table1, column1), (table2, column2))] = similarity
        return formatted_output
