#---------------------------------------------------------------------------

import glob
import json
import argparse
from xoxxox.params import Config

#---------------------------------------------------------------------------

class Custom:

  @staticmethod
  def update(config, dicprm):
    with open(Config.dircnf + "/" + config + Config.expjsn) as f:
      diccnf = json.load(f)
    diccnf.update({k: v for k, v in dicprm.items() if v is not None and v != ""})
    return diccnf

#---------------------------------------------------------------------------

class PrcFlw:

  @staticmethod
  def dicsrv():
    dicsrv = {}
    lstpth = glob.glob(Config.dircnf + "/" + Config.glbsrv)
    for pthcnf in lstpth:
      with open(pthcnf, "r") as f:
        d = json.load(f)
        if isinstance(d, dict):
          dicsrv.update(d)
    return dicsrv
