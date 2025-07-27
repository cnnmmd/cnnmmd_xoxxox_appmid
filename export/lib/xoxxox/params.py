#---------------------------------------------------------------------------
# 参照

import os

#---------------------------------------------------------------------------
# 定義：定数

class Config:
  dircnf = os.getenv("XOXXOX_CNNMMD_SRVCNF")
  expjsn = ".json"
  cnfnet = "xoxxox/cnfnet"
  glbsrv = "*_cnfsrv_*.json"

class SrvMid:
  dirdyn = os.getenv("XOXXOX_CNNMMD_SRVDYN")

class Engine:
  dirprc = os.getenv("XOXXOX_CNNMMD_SRVPRC")

class Medium:
  dirweb = os.getenv("XOXXOX_CNNMMD_SRVWEB")
  ratsmp = 16000
