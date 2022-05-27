from abc import ABC, abstractmethod
import subprocess
import os
from typing import List, Literal, Tuple

INPUT_STRATEGY = "manual"
INPUT_FILENAME = "p2in1.txt"
OUTPUT_FILENAME = "p2out1.txt"
USER_OUTPUT_FILENAME = "output.user.out"
TC_DIR = "test_cases"
CHECKER_FILENAME = "checker.py"
CHECK_STRATEGY = "checker"


class CustomException(Exception):
    """Represent a custom exception"""

    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg


class SubmissionFileNotFound(CustomException):
    """Exception to be raise when submission file is not found"""

    def __init__(self, submission_filename: str):
        super().__init__(f"Submission file {submission_filename} not found")


class TCNotFound(CustomException):
    """Exception to be raise when test case is not found in current directory"""

    def __init__(self, tc_dirname: str):
        super().__init__(f"Test case not found in directory {tc_dirname}")


class InvalidSubmissionFile(CustomException):
    """Exception to be raise when invalid submission file is found"""


class InvalidStrategy(CustomException):
    """Exception to be raised when invalid strategy is found"""


class CheckerNotFound(CustomException):
    """Exception to be raised when checker file is not found"""

    def __init__(self):
        super().__init__("Checker file not found")


class CompilingStrategy(ABC):
    '''

    Represent a generic Compiling Strategy

    Constructor requires 2 parameters:
        filename(str): name of source code file WITHOUT extension
        filename_with_ext(str): name of source code file WITH extension

    '''

    def __init__(self, filename: str, filename_with_ext: str):
        self.filename_without_extension = filename
        self.filename_with_extension = filename_with_ext

    @abstractmethod
    def get_compile_command(self) -> str:
        """Returns compile command for source code file"""

    @abstractmethod
    def get_execute_command(self) -> str:
        """Returns execute command for source code file"""

    @abstractmethod
    def cleanup(self):
        """Clean up files after running submission"""


class CppCompilingStrategy(CompilingStrategy):
    """C++ Compiling Strategy (refer to CompilingStrategy class on how to initialize)"""

    def get_compile_command(self) -> str:
        return f' \
        g++ -std=c++17 -Wshadow -Wall -o \
            "{self.filename_without_extension}" \
                "{self.filename_with_extension}" \
                    -O2 -Wno-unused-result'

    def get_execute_command(self) -> str:
        return f'{self.filename_without_extension}.exe'

    def cleanup(self):
        for file in os.listdir(os.path.join(os.getcwd())):
            if file[-3:] == "exe":
                os.remove(os.path.join(os.getcwd(), file))


class JavaCompilingStrategy(CompilingStrategy):
    """Java Compiling Strategy (refer to CompilingStrategy class on how to initialize)"""

    def get_compile_command(self) -> str:
        return f'javac {self.filename_with_extension}'

    def get_execute_command(self) -> str:
        return f'java {self.filename_without_extension}'

    def cleanup(self):
        for file in os.listdir(os.path.join(os.getcwd())):
            if file[-5:] == "class":
                os.remove(os.path.join(os.getcwd(), file))


class InputStrategy(ABC):
    """Represent a generic Input strategy"""

    def __init__(self, tc_dir: str):
        '''

        Generic initialization of an input strategy
        Generate path of input and user output file and check if input file exists

        '''
        self.input_filepath = os.path.join(tc_dir, INPUT_FILENAME)
        self.user_output_filepath = os.path.join(tc_dir, USER_OUTPUT_FILENAME)

        if not os.path.isfile(self.input_filepath):
            raise TCNotFound(os.path.basename(os.path.normpath(tc_dir)))

    @abstractmethod
    def execute_strategy(self, execute_command: str):
        '''
        Run the provided command inside the environment of an input strategy

        Parameters:
        execute_command(str): command to be executed

        '''


class AutomaticInputStrategy(InputStrategy):
    '''

    Automatic Input strategy
    Use case: When source code is expected to read data from stdin

    '''

    def __init__(self, tc_dir: str):
        super().__init__(tc_dir)
        self.input_fileobj = open(self.input_filepath, encoding='utf-8')
        self.user_output_fileobj = open(
            self.user_output_filepath, 'w', encoding='utf-8')

    def __cleanup(self):
        """Do necessary clean-up after executing the strategy"""
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
            self.temporary_user_output_filepath, 'w', encoding='utf-8')

    def __cleanup(self):
        """Do necessary clean-up after executing the strategy"""
        self.user_output_fileobj.close()
        os.rename(self.temporary_input_filepath, self.input_filepath)
        os.rename(self.temporary_user_output_filepath,
                  self.user_output_filepath)

    def execute_strategy(self, execute_command: str):
        execute_process = subprocess.Popen(
            execute_command, stdout=self.user_output_fileobj, shell=True, cwd=os.getcwd())
        execute_process.wait()
        self.user_output_fileobj.flush()
        self.__cleanup()


class CheckSolutionStrategy(ABC):
    """Represent a strategy used for verifying output produced by source code"""

    def __init__(self, tc_dir: str):
        self.user_output_filepath = os.path.join(tc_dir, USER_OUTPUT_FILENAME)
        self.expected_output_filepath = os.path.join(tc_dir, OUTPUT_FILENAME)

        if not os.path.isfile(self.expected_output_filepath):
            raise TCNotFound(os.path.basename(os.path.normpath(tc_dir)))

        self.user_output_fileobj = None
        self.expected_output_fileobj = None

    def setup_strategy(self):
        """Setup steps needs to be done before verifying solution"""
        self.user_output_fileobj = open(
            self.user_output_filepath, 'r', encoding='utf-8')
        self.expected_output_fileobj = open(
            self.expected_output_filepath, 'r', encoding='utf-8')

    @abstractmethod
    def check_output(self) -> Literal['AC', 'WA']:
        '''

        Determines whether solution is correct

        Returns "AC" if solution is correct, "WA" otherwise

        '''

    @abstractmethod
    def cleanup(self):
        """Clean up stuffs after checking solution"""
        self.user_output_fileobj.close()
        self.expected_output_fileobj.close()
        os.remove(self.user_output_filepath)


class LineCompareCheckStrategy(CheckSolutionStrategy):
    """
    A strategy of verifying solution by checking user output against expected output line by line
    """

    def check_output(self):
        self.setup_strategy()
        verdict = "AC"
        for line in self.expected_output_fileobj:
            user_line = self.user_output_fileobj.readline().rstrip('\r\n')
            expected_line = line.rstrip('\r\n')

            if user_line != expected_line:
                verdict = "WA"
                break

        self.cleanup()
        return verdict


class CheckerCompareCheckStrategy(CheckSolutionStrategy):
    """A strategy of verifying solution using a checker"""

    def __init__(self, tc_dir: str):
        super().__init__(tc_dir)
        self.input_filepath = os.path.join(tc_dir, INPUT_FILENAME)

    def setup_strategy(self):
        checker_filepath = os.path.join(os.getcwd(), CHECKER_FILENAME)
        if not os.path.isfile(checker_filepath):
            raise CheckerNotFound()

    @staticmethod
    def evaluate_python_compiler() -> Literal['python', 'python3']:
        '''Determine the appropriate python compiler based on operating system'''
        return 'python' if (sys.platform == 'win32') else 'python3'

    def run_checker(self) -> int:
        '''
        Run checker with provided input file and output files

        Returns exit code of checker
        '''
        checker_process = subprocess.Popen([
            CheckerCompareCheckStrategy.evaluate_python_compiler(),
            '-u',
            CHECKER_FILENAME,
            self.input_filepath,
            self.user_output_filepath,
            self.expected_output_filepath
        ], cwd=os.getcwd())

        return checker_process.wait()

    def check_output(self):
        checker_exit_code = self.run_checker()
        verdict = 'AC' if (checker_exit_code == 0) else 'WA'
        self.cleanup()
        return verdict

    def cleanup(self):
        os.remove(self.user_output_filepath)


def check_tc(
    execute_command: str,
    input_strategy: InputStrategy,
    check_strategy: CheckSolutionStrategy
):
    '''
    Run user's code against provided a test case

    Parameters:
    execute_command (str): Command used to execute file generated from
    compilation of submission file
    input_strategy (InputStrategy): Input strategy that is used for this source code
    check_strategy (CheckSolutionStrategy): Strategy used by source code to verify correctness

    '''
    input_strategy.execute_strategy(execute_command)

    # Get verdict by checking user output against expected output
    tc_verdict = check_strategy.check_output()

    return tc_verdict


def compile_submission(compile_command: str):
    """Compile user submission"""
    subprocess.call(compile_command, shell=True, cwd=os.getcwd())


def evaluate_submission(compiling_strategy: CompilingStrategy):
    '''
    Evaluate provided submission file by running it against provided test cases

    Parameters:
    compiling_strategy (CompilingStrategy): Compiling strategy used by source code

    '''
    compile_command = compiling_strategy.get_compile_command()
    execute_command = compiling_strategy.get_execute_command()

    # Compile user submission
    compile_submission(compile_command)

    verdict_list = []

    # Loop through each test case directory and get verdict of that test case
    for directory in os.listdir(os.path.join(os.getcwd(), TC_DIR)):
        tc_dir = os.path.join(os.getcwd(), TC_DIR, directory)
        tc_verdict = check_tc(execute_command, get_input_strategy(
            tc_dir), get_check_solution_strategy(tc_dir))
        verdict_list.append((directory, tc_verdict))

    # Print verdict of all test cases
    print_verdict(verdict_list)

    # Clean up
    compiling_strategy.cleanup()


def print_verdict(verdict_list: List[Tuple[str, str]]):
    '''
    Print test case verdict with appropriate format

    Parameters:
    verdict_list(list[str]): list of verdicts

    '''
    print()
    for (directory, verdict) in verdict_list:
        passed = verdict.rstrip('\r\n') == "AC"

        if not passed:
            msg = f" x Test case {directory} failed"
            print(f"\033[91m{msg}\033[00m")
        else:
            msg = f"Test case {directory} passed"
            print(f"\033[92m{msg}\033[00m")
        sys.stdout.flush()
    print()


def get_compiling_strategy(filename_without_extension: str, extension: str) -> CompilingStrategy:
    '''

    Generate a compiling strategy based on extension of source code file

    Parameters:
    filename_without_extension: file name of the source code file without extension
    extension: extension of the source code file

    '''
    instance_factory = {
        '.cpp': CppCompilingStrategy,
        '.java': JavaCompilingStrategy
    }

    if extension not in instance_factory:
        raise InvalidSubmissionFile("Extension is not supported")

    return instance_factory[extension](
        filename_without_extension,
        filename_without_extension + extension
    )


def get_input_strategy(tc_dir: str) -> InputStrategy:
    '''

    Generate input strategy based on configuration

    Parameters:
    tc_dir(str): directory of current test case

    '''
    instance_factory = {
        'automatic': AutomaticInputStrategy,
        'manual': ManualInputStrategy
    }

    if INPUT_STRATEGY not in instance_factory:
        raise InvalidStrategy(f'Input strategy {INPUT_STRATEGY} not supported')

    return instance_factory[INPUT_STRATEGY](tc_dir)


def get_check_solution_strategy(tc_dir: str) -> CheckSolutionStrategy:
    '''

    Generate a strategy to verify solution

    Parameters:
    tc_dir(str): directory of current test case

    '''
    instance_factory = {
        'line': LineCompareCheckStrategy,
        'checker': CheckerCompareCheckStrategy
    }

    if CHECK_STRATEGY not in instance_factory:
        raise InvalidStrategy("Check Solution Strategy not found")

    return instance_factory[CHECK_STRATEGY](tc_dir)


def check_valid_file(filename: str):
    '''
    Check if submission file is a valid file
    If file is valid, return filename (without extension) and extension as tuple of strings

    Parameters:
    filename(str): filename with extension of user source code
    '''
    # Extract file extension
    idx = filename.find('.')

    # If there is no extension
    if idx == -1:
        raise InvalidSubmissionFile("Extension not included")

    # If filename only contains extension
    if idx == 0:
        raise InvalidSubmissionFile("File name not found")

    # Check if file exists
    filepath = os.path.join(os.getcwd(), filename)
    if not os.path.isfile(filepath):
        raise SubmissionFileNotFound(filename)

    return filename[:idx], filename[idx:]


def main():
    """Driver code"""
    # Prompt for submission's filename
    print("Enter filename: ", end='')
    input_file = input()

    filename_without_extension, extension = check_valid_file(input_file)

    # Generate compiling strategy for source code
    compiling_strategy = get_compiling_strategy(
        filename_without_extension, extension)

    # Evaluate source code
    evaluate_submission(compiling_strategy)


if __name__ == '__main__':
    import sys
    try:
        sys.exit(main())
    except CustomException as err:
        print(f"\033[91m{err.msg}\033[00m")
        sys.exit(1)
