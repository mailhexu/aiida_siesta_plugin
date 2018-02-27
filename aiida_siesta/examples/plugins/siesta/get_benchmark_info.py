#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-
import sys
import os

__copyright__ = u"Copyright (c), This file is part of the AiiDA platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.7.0"
__authors__ = "The AiiDA team."

#
# Prints benchmark info for a calculation
#

# Used to test the parent calculation
SiestaCalc = CalculationFactory('siesta.siesta') 

try:
    calc_id = sys.argv[1]
except IndexError:
    print >> sys.stderr, ("Must provide as parameter the calc ID")
    sys.exit(1)


try:
    int(calc_id)
except ValueError:
    raise ValueError('Calc_id not an integer: {}'.format(calc_id))

calc = load_node(int(calc_id))

if isinstance(calc,SiestaCalc):

    print "Calculation status: '{}'".format(calc.get_state())
    print "Desc: {}".format(calc.description)
    d=calc.out.output_parameters.get_dict()
    
    try:
        no_u = d['no_u']
        nnz = d['nnz']
        print "No of orbitals: {} nnz: {}".format(no_u,nnz)
        sys.stderr.write("{} {}".format(no_u,nnz))
    except:
        pass
    try:
        mesh = d['mesh']
        np = mesh[0]*mesh[1]*mesh[2]
        print "Mesh points: {} (total {})".format(mesh,np)
        sys.stderr.write(" {} {}".format(mesh,np))
    except:
        pass
    try:
        nodes= d['siesta:Nodes']
        print "Number of nodes {}".format(nodes)
        sys.stderr.write(" {} ".format(int(nodes)))
    except:
        pass
    try:
        code= str(calc.get_code()).split()[2]
        print "Code: {}".format(code)
        sys.stderr.write(" {} ".format(code))
    except:
        pass
    try:
        computer= str(calc.get_computer()).split()[0]
        print "Computer: {}".format(computer)
        sys.stderr.write(" {} ".format(computer))
    except:
        pass
    try:
        t_global = d['global_time']
        print "Total time: {}".format(t_global)
    except:
        pass

    try:
        t_decomp = d['timing_decomposition']
        t_solver = t_decomp['compute_DM']
        t_H = t_decomp['setup_H']
        print "Total time, solver, setup_H: {} {} {}".format(t_global,t_solver,t_H)
        sys.stderr.write(" {} {} {}\n".format(t_global,t_solver,t_H))
    except:
        pass
    
        sys.stderr.flush()

else:
    print >> sys.stderr, ("Calculation should be a Siesta calculation.")
    sys.exit(1)



