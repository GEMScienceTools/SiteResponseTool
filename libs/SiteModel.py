# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 GEM Foundation
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>.
#
# Author: Poggi Valerio

'''
Collection of base classes to create and manipulate site models.
'''

import numpy as np
import SiteMethods as SM
import AsciiTools as AT

class Site1D(object):
  '''
  SINGLE SITE ELEMENT (ONE-DIMENSIONAL)
  The object is structured to act as minimal database for
  soil properties, site metadata and methods to compute
  site parameters (Vs30, amplification...)
  '''


  def __init__(self, Id=[],
                     Name=[],
                     Longitude=[],
                     Latitude=[],
                     Elevation=[],
                     Keys=['Hl','Vp','Vs','Dn','Qp','Qs']):

    self.Meta = {'Id': Id,
                 'Name': Name,
                 'Longitude': Longitude,
                 'Latitude': Latitude,
                 'Elevation': Elevation}

    self.Keys = Keys
    self.Layer = []

    self.EngPar = {}
    self.EngPar['Vz'] = {}
    self.EngPar['Qwl'] = {}


  def AddLayer(self, Data=[]):
    '''
    
    Method to add a single layer (and its properties)
    to the site structure, at the bottom of an existing stack.
    Data can be a list of values, sorted according to Site1D.Keys
    or a dictionary element with corresponding format.
    '''

    LS = {}

    # Inflate the layer structure with data (if any)

    if type(Data) is list:
      for i, k in enumerate(self.Keys):
        if Data:
          LS[k] = Data[i]
        else:
          LS[k] = []

    if type(Data) is dict:
      for k in Data.keys():
        LS[k] = Data[k]

    # Add the new layer structure to the layer stack
    self.Layer.append(LS)


  def Size(self):
    '''
    Method to return size of the data matrix.
    '''

    lnum = len(self.Layer)
    knum = len(self.Keys)

    return [lnum, knum]


  def ImportModel(self, ascii_file,
                        read_header='yes',
                        dtype='float',
                        delimiter=',',
                        skipline=0,
                        comment='#'):
    '''
    Method to parse soil properties from an ascii file.
    '''

    if read_header == 'yes':
      header = []

    if read_header == 'no':
      header = self.Keys

    at = AT.AsciiTable()
    at.Import(ascii_file, header=header,
                          dtype=dtype,
                          delimiter=delimiter,
                          skipline=skipline,
                          comment=comment)

    self.Keys = at.header
    self.Layer = at.data


  def GetProfile(self, key):
    '''
    Method to extract a column of soil properties from
    the layer stack. It returns a numpy array.
    '''

    return np.array([i[key] for i in self.Layer])


  def ComputeTTAV(self, key, Z):
    '''
    Compute and store travel-time average velocity at
    a given depth (Z) and for a specific key.
    '''

    Hl = self.GetProfile('Hl')
    Vl = self.GetProfile(key)

    Vz = SM.TTAverageVelocity(Hl, Vl, Z)

    self.EngPar['Vz'][str(Z)] = Vz

    return Vz


  def ComputeSHTF(self, Freq, Iang):
    '''
    Compute the SH transfer function.
    '''

    Hl = self.GetProfile('Hl')
    Vs = self.GetProfile('Vs')
    Dn = self.GetProfile('Dn')
    Qs = self.GetProfile('Qs')

    shtf = SM.ShTransferFunction(Hl, Vs, Dn, Qs, Freq, Iang)

    return shtf


class SiteBox(object):
  '''
  A simple container class to group sites of a region
  '''

  def __init__(self, Id=[],
                     Name=[]):

    self.Meta = {'Id': Id,
                 'Name': Name}

    self.Site = []
    self.Size = 0


  def AddSite(self, Site1D):
    '''
    Method to just add a single site object to the container.
    '''

    self.Site.append(Site1D)
    self.Size += 1

