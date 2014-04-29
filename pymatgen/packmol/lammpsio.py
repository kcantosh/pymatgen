#!/usr/bin/env python

import re
import numpy as np
from pymatgen.serializers.json_coders import MSONable


class LammpsLog(MSONable):
    """
    Parser for LAMMPS log file (parse function).
    Saves the output properties (log file) in the form of a dictionary (LOG) with the key being
    the LAMMPS output property (see 'thermo_style custom' command in the LAMMPS documentation).
    For example, LOG['temp'] will return the temperature data array in the log file.
    """

    def __init__(self, filename):
        """
        Args:
            filename:
                Filename of the LAMMPS logfile.
        """

        self.filename = filename
        self.log = {}  # Dictionary LOG has all the output property data as numpy 1D arrays with the property name as the key
        self.ave = {}
        self.header = 0
        self.footer_blank_line = 0  # blank lines in footer

    def _list2float(self, seq):
        for x in seq:
            try:
                yield float(x)
            except ValueError:
                yield x

    def parselog(self):
        """
        Parses the log file. 
        """
        md = 0  #To avoid reading the minimization data steps

        with open(self.filename, 'r') as logfile:
            self.total_lines = len(logfile.readlines())
        logfile.close

        with open(self.filename, 'r') as logfile:

            for line in logfile:

                # total steps of MD
                steps = re.search('run\s+([0-9]+)', line)
                if steps:
                    self.md_step = float(steps.group(1))
                    md = 1

                # save freq to log
                thermo = re.search('thermo\s+([0-9]+)', line)
                if thermo:
                    self.log_save_freq = float(thermo.group(1))

                # log format
                format = re.search('thermo_style.+', line)
                if format:
                    data_format = format.group().split()[2:]

                if all(isinstance(x, float) for x in
                       list(self._list2float(line.split()))) and md == 1: break
                self.header = self.header + 1

            for line in logfile:
                if (line == '\n'): self.footer_blank_line = self.footer_blank_line + 1

                #print self.total_lines
                #print self.md_step
                #print self.log_save_freq
                #print self.footer_blank_line

        rawdata = np.genfromtxt(fname=self.filename, dtype=float, skip_header=int(self.header),
                                skip_footer=int(self.total_lines - (
                                self.header + self.md_step / self.log_save_freq + 1) - self.footer_blank_line))
        #print rawdata

        for column, property in enumerate(data_format):
            self.log[property] = rawdata[:, column]

        # calculate the average
        for key in self.log.keys():
            #print key
            #print self.LOG[key]
            self.ave[str(key)] = np.mean(self.log[key])

    def list_properties(self):
        """
        print the list of properties
        """
        #print log.LOG.keys()
        pass

    @property
    def to_dict(self):
        return {{"@module": self.__class__.__module__,
                 "@class": self.__class__.__name__} + self.log}


    @classmethod
    def from_dict(cls, d):
        return LammpsLog(**d)


if __name__ == '__main__':
    filename = 'log.test'
    log = LammpsLog(filename)
    log.parselog()
    #print log.LOG.keys()
    #print log.LOG
    log.list_properties()
    #print np.mean(log.LOG['step'])
    #print log.ave['step']
                    
        
        
         
    
    