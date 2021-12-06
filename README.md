# Mini-Judge

## Update

-   Mini-Judge now supports Checker Strategy for validating solution correctness, which can be used when solution correctness cannot be determined using Line by Line strategy.

## Introduction

-   A Python script that will automatically run your source code against a set of provided test cases.
-   Currently supports Java and C++.

## Requirements:

-   Python 3
-   Java (and/or C++) compiler

## Setup Guide

-   In the same directory as that which has the `.py` script, create a new folder called `test_cases`.
-   Place the source code that you want to test in the same directory as that containing the `.py` and `test_cases`.

## To create a test case

-   Create a new subfolder inside the `test_cases` directory.
-   Inside the new subfolder, create 2 new files with the following names:
    -   `p2in1.txt`: This will be the name of the input file.
    -   `p2out1.txt`: This will be the name of the expected output file.

## To run test case check

-   Make sure that all the steps in [Setup Guide](#setup-guide) are completed.
-   Compile and execute the script file.

## To change input strategy:

-   Inside `cmd_script.py` file, do the following:
    -   Switch to <b>Automatic Input Strategy</b>: Change the value of `INPUT_STRATEGY` constant variable to `automatic`
    -   Switch to <b>Manual Input Strategy</b>: Change the value of `INPUT_STRATEGY` constant variable to `manual`
