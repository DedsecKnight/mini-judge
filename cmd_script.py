'''

To change compile command, modify the return value of get_compile_command function for the strategy that you will be using
    e.g: If your code is written in C++, you can modify return value of get_compile_command function of the CppCompilingStrategy class. 
        Same goes for Java users

To change execute command, do the same with changing compile command, but with the get_execute_command function of respective strategy

Some notes before using: 
    - It may takes some time to run through all the test cases
    - Before running your source code against this script, make sure that your code will read input from stdin instead of from the text file
    

'''
from io import TextIOWrapper
from abc import ABC, abstractmethod
import subprocess
import os
from typing import List

INPUT_STRATEGY = "manual"
INPUT_FILENAME = "p2in1.txt"
OUTPUT_FILENAME = "p2out1.txt"
USER_OUTPUT_FILENAME = "output.user.out"
TC_DIR = "test_cases"


class CustomException(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class SubmissionFileNotFound(CustomException):
    def __init__(self, submission_filename: str):
        super().__init__(f"Submission file {submission_filename} not found")


class TCNotFound(CustomException):
    def __init__(self, tc_dirname: str):
        super().__init__(f"Test case not found in directory {tc_dirname}")


class InvalidSubmissionFile(CustomException):
    def __init__(self, err_msg: str):
        super().__init__(err_msg)


class InvalidStrategy(CustomException):
    def __init__(self, err_msg):
        super().__init__(err_msg)


class CompilingStrategy(ABC):
    '''

    Represent a generic Compiling Strategy

    Constructor requires 2 parameters:
        filename(str): name of source code file WITHOUT extension
        filename_with_ext(str): name of source code file WITH extension 

    Functions:
        get_compile_command(): returns compile command for source code file
        get_execute_command(): returns execute command for executable file

    '''

    def __init__(self, filename: str, filename_with_ext: str):
        self.filename_without_extension = filename
        self.filename_with_extension = filename_with_ext

    @abstractmethod
    def get_compile_command(self) -> str:
        pass

    @abstractmethod
    def get_execute_command(self) -> str:
        pass


class CppCompilingStrategy(CompilingStrategy):
    '''

    C++ Compiling Strategy (refer to CompilingStrategy class on how to initialize)

    '''

    def __init__(self, filename: str, filename_with_ext: str):
        super().__init__(filename, filename_with_ext)

    def get_compile_command(self) -> str:
        return f'g++ -std=c++17 -Wshadow -Wall -o "{self.filename_without_extension}" "{self.filename_with_extension}" -O2 -Wno-unused-result'

    def get_execute_command(self) -> str:
        return f'{self.filename_without_extension}.exe'


class JavaCompilingStrategy(CompilingStrategy):
    '''

    Java Compiling Strategy (refer to CompilingStrategy class on how to initialize)

    '''

    def __init__(self, filename: str, filename_with_ext: str):
        super().__init__(filename, filename_with_ext)

    def get_compile_command(self) -> str:
        return f'javac {self.filename_with_extension}'

    def get_execute_command(self) -> str:
        return f'java {self.filename_without_extension}'


class InputStrategy(ABC):
    '''
    Represent a generic Input strategy
    '''

    def __init__(self, tc_dir: str):
        '''

        Generic initialization of an input strategy
        Generate path of input and user output file and check if input file exists

        '''
        self.input_filepath = os.path.join(tc_dir, INPUT_FILENAME)
        self.user_output_filepath = os.path.join(tc_dir, USER_OUTPUT_FILENAME)

        if (not os.path.isfile(self.input_filepath)):
            raise TCNotFound(os.path.basename(os.path.normpath(tc_dir)))

    @abstractmethod
    def execute_strategy(self, execute_command: str):
        '''
        Run the provided command inside the environment of an input strategy

        Parameters:
        execute_command(str): command to be executed

        '''
        pass


class AutomaticInputStrategy(InputStrategy):
    '''

    Automatic Input strategy
    Use case: When source code is expected to read data from stdin

    '''

    def __init__(self, tc_dir: str):
        super().__init__(tc_dir)
        self.input_fileobj = open(self.input_filepath)
        self.user_output_fileobj = open(self.user_output_filepath, 'w')

    def __cleanup(self):
        '''

        Do necessary clean-up after executing the strategy

        '''
        self.input_fileobj.close()
        self.user_output_fileobj.close()

    def execute_strategy(self, execute_command: str):
        p = subprocess.Popen(execute_command, stdin=self.input_fileobj,
                             stdout=self.user_output_fileobj, shell=True, cwd=os.getcwd())
        p.wait()
        self.user_output_fileobj.flush()
        self.__cleanup()


class ManualInputStrategy(InputStrategy):
    '''

    Manual Input Strategy
    Use case: When source code is expected to read data directly from text file 

    '''

    def __init__(self, tc_dir: str):
        super().__init__(tc_dir)
        self.temporary_input_filepath = os.path.join(
            os.getcwd(), INPUT_FILENAME)
        self.temporary_user_output_filepath = os.path.join(
            os.getcwd(), USER_OUTPUT_FILENAME)

        os.rename(self.input_filepath, self.temporary_input_filepath)
        self.user_output_fileobj = open(
            self.temporary_user_output_filepath, 'w')

    def __cleanup(self):
        '''

        Do necessary clean-up after executing the strategy

        '''
        self.user_output_fileobj.close()
        os.rename(self.temporary_input_filepath, self.input_filepath)
        os.rename(self.temporary_user_output_filepath,
                  self.user_output_filepath)

    def execute_strategy(self, execute_command: str):
        p = subprocess.Popen(
            execute_command, stdout=self.user_output_fileobj, shell=True, cwd=os.getcwd())
        p.wait()
        self.user_output_fileobj.flush()
        self.__cleanup()


def check_output(user_output: TextIOWrapper, expected_output: TextIOWrapper) -> str:
    '''
    Compare output produced by user against expected output

    Parameters:
    user_output (TextIOWrapper): File containing output produced by submission file
    expected_output (TextIOWrapper): File containing expected output

    '''
    for line in expected_output:
        user_line = user_output.readline().rstrip('\r\n')
        expected_line = line.rstrip('\r\n')

        if (user_line != expected_line):
            return "WA"

    return "AC"


def check_tc(execute_command: str, tc_dir: str, input_strategy: InputStrategy):
    '''
    Run user's code against provided a test case

    Parameters:
    execute_command (str): Command used to execute file generated from compilation of submission file
    tc_dir (str): Directory of current test case

    '''
    output_name = os.path.join(tc_dir, 'output.user.out')
    expected_output_path = os.path.join(tc_dir, OUTPUT_FILENAME)

    if (not os.path.isfile(expected_output_path)):
        raise TCNotFound(os.path.basename(os.path.normpath(tc_dir)))

    input_strategy.execute_strategy(execute_command)

    # Open user output and expected output file
    user_output = open(output_name, 'r')
    expected_output = open(expected_output_path, 'r')

    # Get verdict by checking user output against expected output
    tc_verdict = check_output(user_output, expected_output)

    user_output.close()
    expected_output.close()

    # Remove user output file
    os.remove(output_name)

    return tc_verdict


def evaluate_submission(submission_filename: str, compiling_strategy: CompilingStrategy):
    '''
    Evaluate provided submission file by running it against provided test cases

    Parameters:
    submission_filename (str): Name of submission file
    compile_command (str): Command used to compile submission file
    execute_command (str): Command used to execute submission file

    '''
    compile_command = compiling_strategy.get_compile_command()
    execute_command = compiling_strategy.get_execute_command()

    verdict_list = []

    # Get file path of source code file
    submission_path = os.path.join(os.getcwd(), submission_filename)

    # Raise error if source code file is not found
    if (not os.path.isfile(submission_path)):
        raise SubmissionFileNotFound(submission_filename)

    # Compile user's submission
    subprocess.call(compile_command, shell=True, cwd=os.getcwd())

    # Loop through each test case directory and get verdict of that test case
    for directory in os.listdir(os.path.join(os.getcwd(), TC_DIR)):
        tc_dir = os.path.join(os.getcwd(), TC_DIR, directory)
        tc_verdict = check_tc(execute_command, tc_dir,
                              get_input_strategy(tc_dir))
        verdict_list.append(tc_verdict)

    print_verdict(verdict_list)


def print_verdict(verdict_list: List[str]):
    '''
    Print test case verdict with appropriate format

    Parameters:
    verdict_list(list[str]): list of verdicts

    '''
    print()
    for (tc_idx, verdict) in enumerate(verdict_list):
        passed = verdict.rstrip('\r\n') == "AC"

        if (not passed):
            print("\033[91m{}\033[00m".format(
                " x Test case #" + str(tc_idx+1) + " failed"))
        else:
            print("\033[92m{}\033[00m".format(
                "Test case #" + str(tc_idx+1) + " passed"))
        sys.stdout.flush()
    print()


def get_compiling_strategy(filename_without_extension: str, extension: str) -> CompilingStrategy:
    '''

    Generate a compiling strategy based on extension of source code file

    Parameters: 
    filename_without_extension: file name of the source code file without extension
    extension: extension of the source code file

    '''
    if (extension == '.cpp'):
        return CppCompilingStrategy(filename_without_extension, filename_without_extension + extension)
    if (extension == '.java'):
        return JavaCompilingStrategy(filename_without_extension, filename_without_extension + extension)
    raise InvalidSubmissionFile("Extension is not supported")


def get_input_strategy(tc_dir: str) -> InputStrategy:
    '''

    Generate input strategy based on configuration

    '''
    if (INPUT_STRATEGY == "automatic"):
        return AutomaticInputStrategy(tc_dir)
    if (INPUT_STRATEGY == "manual"):
        return ManualInputStrategy(tc_dir)
    raise InvalidStrategy(f'Input strategy {INPUT_STRATEGY} not supported')


def main(args):
    # Prompt for submission's filename
    print("Enter filename: ", end='')
    input_file = input()

    # Extract file extension
    idx = input_file.find('.')

    # If there is no extension
    if (idx == -1):
        raise InvalidSubmissionFile("Extension not included")

    # If filename only contains extension
    if (idx == 0):
        raise InvalidSubmissionFile("File name not found")

    # Generate compiling strategy for source code
    compiling_strategy = get_compiling_strategy(
        input_file[:idx], input_file[idx:])

    # Evaluate source code
    evaluate_submission(input_file, compiling_strategy)


if __name__ == '__main__':
    import sys
    try:
        sys.exit(main(sys.argv))
    except CustomException as err:
        print("\033[91m{}\033[00m" .format(
            err.msg))
        exit(1)
