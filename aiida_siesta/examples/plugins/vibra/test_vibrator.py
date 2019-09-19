#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
import six
__copyright__ = u"Copyright (c), 2015, ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE (Theory and Simulation of Materials (THEOS) and National Centre for Computational Design and Discovery of Novel Materials (NCCR MARVEL)), Switzerland and ROBERT BOSCH LLC, USA. All rights reserved."
__license__ = "MIT license, see LICENSE.txt file"
__version__ = "0.7.0"
__contributors__ = "Andrea Cepellotti, Victor Garcia-Suarez, Alberto Garcia"

import sys
import os

from aiida.common.example_helpers import test_and_get_code
from aiida.common.exceptions import NotExistent
from aiida.orm import CalculationFactory

################################################################
ParameterData = DataFactory('parameter')
KpointsData = DataFactory('array.kpoints')
StructureData = DataFactory('structure')
SinglefileData = DataFactory('singlefile')

try:
    dontsend = sys.argv[1]
    if dontsend == "--dont-send":
        submit_test = True
    elif dontsend == "--send":
        submit_test = False
    else:
        raise IndexError
except IndexError:
    print(("The first parameter can only be either "
                          "--send or --dont-send"), file=sys.stderr)
    sys.exit(1)

try:
    codename = sys.argv[2]
except IndexError:
    codename = 'vib-4.0.1@cm135'

code = test_and_get_code(codename, expected_code_type='siesta.vibrator')
#
#  Set up calculation object first
#
calc = code.new_calc()
calc.label = "Test Vibrator. Bulk silicon"
calc.description = "Test calculation with the Vibrator code. Bulk silicon"

#
#----Settings first  -----------------------------
#
settings_dict={}
settings = ParameterData(dict=settings_dict)
calc.use_settings(settings)
#---------------------------------------------------

#
# Structure -----------------------------------------
#
alat = 5.43 # Angstrom. Not passed to the fdf file (only for internal use)
cell = [[0., alat/2, alat/2,],
        [alat/2, 0., alat/2,],
        [alat/2, alat/2, 0.,],]
sicd = alat*0.125

s = StructureData(cell=cell)
s.append_atom(position=(sicd,sicd,sicd),symbols=['Si'])
s.append_atom(position=(-sicd,-sicd,-sicd),symbols=['Si'])

elements = list(s.get_symbols_set())
calc.use_structure(s)
#-------------------------------------------------------------

#
# Parameters ---------------------------------------------------
#
params_dict= {
'SuperCell_1': 1,
'SuperCell_2': 1,
'SuperCell_3': 1,
'AtomicDispl': '0.021 Ang'
}
# Replace '.' with '_' for the database
params_dict = { k.replace('.','-') :v for k,v in six.iteritems(params_dict) }
parameters = ParameterData(dict=params_dict)
calc.use_parameters(parameters)

#
# K-points for bands --------------------
bandskpoints = KpointsData()

kpp = [(1,2.,2.,2.),
       (15,2.,0.,0.),
       (25,0.,0.,0.),
       (20,1.,1.,1.),
       (20,2.,0.,0.),
       (15,2.,1.,0.),
       (20,1.,1.,1.)]
lpp = [[0,'\Gamma'],
       [1,'X'],
       [2,'\Gamma'],
       [3,'L'],
       [4,'X'],
       [5,'W'],
       [6,'L']]
bandskpoints.set_cell(s.cell, s.pbc)
bandskpoints.set_kpoints(kpp,labels=lpp)

calc.use_bandskpoints(bandskpoints)

#----------------------------------------------------------
#
absname = os.path.realpath(os.path.join(os.path.dirname(__file__),"data"))+'/aiida.FC'
filefc = SinglefileData()
filefc.add_path(absname)
calc.use_singlefile(filefc)

#from aiida.orm.data.remote import RemoteData
#calc.set_outdir(remotedata)

#calc.set_resources({"num_machines": 1, "num_mpiprocs_per_machine": 2})
calc.set_resources({"parallel_env": 'mpi', "tot_num_mpiprocs": 1})
code_mpi_enabled =  False
try:
    code_mpi_enabled =  code.get_extra("mpi")
except AttributeError:
    pass
calc.set_withmpi(code_mpi_enabled)
#------------------
queue = None
# calc.set_queue_name(queue)
#------------------

if submit_test:
    subfolder, script_filename = calc.submit_test()
    print("Test_submit for calculation (uuid='{}')".format(
        calc.uuid))
    print("Submit file in {}".format(os.path.join(
        os.path.relpath(subfolder.abspath),
        script_filename
        )))
else:
    calc.store_all()
    print("created calculation; calc=Calculation(uuid='{}') # ID={}".format(
        calc.uuid,calc.dbnode.pk))
    calc.submit()
    print("submitted calculation; calc=Calculation(uuid='{}') # ID={}".format(
        calc.uuid,calc.dbnode.pk))

