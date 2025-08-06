#---------------------------------------------------------------------------
# 参照

from uuid6 import uuid7
import json
import asyncio
from aiohttp import web
import argparse
import importlib
import pkgutil
from xoxxox.shared import Custom
from xoxxox.libmid import LibMid
from xoxxox.params import SrvMid

#---------------------------------------------------------------------------
# 参照：拡張／プラグイン

for _, p, f in pkgutil.iter_modules([SrvMid.dirdyn]):
  if f:
    LibMid.plugin[p] = importlib.import_module(p)

#---------------------------------------------------------------------------
# 評価：拡張／プラグイン
# 処理：メソッドに渡す引数の評価値（次の順番で引き渡し）：
# argtgt ... "arg": [...] ... LibMid.values[dicreq[X]] # ラベルのデータ
# cnftgt ... "cnf": [...] ... dicreq[X] # ラベル

def invoke(frmtgt, argtgt, cnftgt, dicreq):
  p, c, m = frmtgt.split(".")
  module = LibMid.plugin[p]
  clstgt = getattr(module, c)
  method = getattr(clstgt, m)
  lstarg = [LibMid.values[dicreq[i]] for i in argtgt]
  lstarg.extend([dicreq[i] for i in cnftgt])
  result = method(*lstarg)
  return result

#---------------------------------------------------------------------------
# 初期

async def resini(datreq):
  global numset
  global numget
  global lstset
  global lstget

  dicreq = await datreq.json()

  LibMid.values = {}
  for i in range(numset):
    keyset = f"{i:03}"
    lstset[keyset] = []
    evtset[keyset].clear()
  for i in range(numget):
    keyget = f"{i:03}"
    lstget[keyget] = []
    evtget[keyset].clear()

  return web.Response(
    text=json.dumps({keysts: "0"}),
    headers={
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': dicnet["adraco"]
    }
  )

#---------------------------------------------------------------------------
# 格納：内容を受信〜内容を格納〜キーを送信

async def resset(datreq):
  keydat = str(uuid7())
  LibMid.values[keydat] = await datreq.read()

  return web.Response(
    text=json.dumps({keysts: "0", keyddt: keydat}),
    headers={
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': dicnet["adraco"]
    }
  )

#---------------------------------------------------------------------------
# 取得：キーを受信〜内容を取得〜内容を送信

async def resget(datreq):
  dicreq = await datreq.json()
  keydat = dicreq[keyddt]

  return web.Response(
    body=LibMid.values[keydat],
    headers={
      'Content-Type': 'application/octet-stream',
      'Access-Control-Allow-Origin': dicnet["adraco"]
    }
  )

#---------------------------------------------------------------------------
# 格納：ローデータを受け取り（受信完了を通知）

async def ressps(datreq):
  global lstset
  global evtset

  keydat = str(uuid7())
  LibMid.values[keydat] = await datreq.read()

  pthset = datreq.path
  keyset = pthset[4:]
  lstset[keyset].append(keydat)

  evtset[keyset].set() # EVT

  return web.Response(
    text=json.dumps({keysts: "0"}),
    headers={
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': dicnet["adraco"]
    }
  )

#---------------------------------------------------------------------------
# 格納：データＩＤを引き渡し（準備ができたら）

async def resspp(datreq):
  global lstset
  global evtset

  pthset = datreq.path
  keyset = pthset[4:]
  await evtset[keyset].wait() # EVT
  evtset[keyset].clear() # EVT

  keydat = lstset[keyset].pop()

  return web.Response(
    text=json.dumps({keysts: "0", keyddt: keydat}),
    headers={
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': dicnet["adraco"]
    }
  )

#---------------------------------------------------------------------------
# 取得：データＩＤを受け取り（受信完了を通知）

async def resgps(datreq):
  global lstget
  global evtget

  dicreq = await datreq.json()
  keydat = dicreq[keyddt]

  pthget = datreq.path
  keyget = pthget[4:]
  lstget[keyget].append(keydat)

  evtget[keyget].set() # EVT

  return web.Response(
    text=json.dumps({keysts: "0"}),
    headers={
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': dicnet["adraco"]
    }
  )

#---------------------------------------------------------------------------
# 取得：ローデータを引き渡し（準備ができたら）

async def resgpp(datreq):
  global lstget
  global evtget

  pthget = datreq.path
  keyget = pthget[4:]
  await evtget[keyget].wait() # EVT
  evtget[keyget].clear() # EVT

  keydat = lstget[keyget].pop()

  return web.Response(
    body=LibMid.values[keydat],
    headers={
      'Content-Type': 'application/octet-stream',
      'Access-Control-Allow-Origin': dicnet["adraco"]
    }
  )

#---------------------------------------------------------------------------
# 処理

async def resprc(datreq):
  dicreq = await datreq.json()

  # コードを評価（動的コード："keyprc"）
  keyprc = dicreq[keydpr]
  frmtgt = LibMid.dicprc[keyprc][prcfrm]
  try:
    argtgt = LibMid.dicprc[keyprc][prcarg]
  except Exception:
    argtgt = []
  try:
    cnftgt = LibMid.dicprc[keyprc][prccnf]
  except Exception:
    cnftgt = []
  if LibMid.dicprc[keyprc][prcsyn] == True:
    try:
      result = invoke(frmtgt, argtgt, cnftgt, dicreq)
    except Exception as e:
      print(f"err: srvmid: syn: {e}", flush=True)
  else:
    try:
      result = await invoke(frmtgt, argtgt, cnftgt, dicreq)
    except Exception as e:
      print(f"err: srvmid: asy: {e}", flush=True)

  # 値を格納（ラベル（タプルでない："keydat"、タプルである："keyNNN"））
  dicres = {}
  if isinstance(result, tuple):
    for i in result:
      keydat = str(uuid7())
      LibMid.values[keydat] = i
      numkey = f"{i:03}"
      dicres[keydtp + numkey] = keydat
    dicres[keysts] = str(len(result))
  else:
    keydat = str(uuid7())
    LibMid.values[keydat] = result
    dicres[keyddt] = keydat
    dicres[keysts] = "0"

  # 値のラベルを返却
  return web.Response(
    text=json.dumps(dicres),
    headers={
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': dicnet["adraco"]
    }
  )

#---------------------------------------------------------------------------
# 予備応答（プリフライト：ポスト）

async def optpre(datreq):
  return web.Response(
    headers={
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Allow-Origin': dicnet["adraco"]
    }
  )

#---------------------------------------------------------------------------
# 引数

parser = argparse.ArgumentParser()
parser.add_argument("--secure", default="0")
parser.add_argument("--svport", type=int, default="80")
parser.add_argument("--numset", type=int, default="1")
parser.add_argument("--numget", type=int, default="1")
parser.add_argument("--adraco", type=str) # default: cnfnet
parser.add_argument("--pthcrt", type=str) # default: cnfnet
parser.add_argument("--pthkey", type=str) # default: cnfnet
objarg = parser.parse_args()

cnfnet = "xoxxox/cnfnet"
dicnet = Custom.update(cnfnet, {k: v for k, v in vars(objarg).items() if v is not None})

secure = objarg.secure
svport = objarg.svport
numset = int(objarg.numset)
numget = int(objarg.numget)

#---------------------------------------------------------------------------
# 変数

lstset = {} # ディクショナリ：内容を格納するリスト、次で使用：sps/spp
lstget = {} # ディクショナリ：内容を格納するリスト、次で使用：gps/gpp
evtset = {} # ディクショナリ：イベント、次で使用：sps/spp
evtget = {} # ディクショナリ：イベント、次で使用：gps/gpp

keysts = "status" # ステータスの辞書キー
keydpr = "keyprc" # 動的コードの辞書キー
keyddt = "keydat" # データキーの辞書キー（処理の場合：タプルでないとき）
keydtp = "key"    # データキーの辞書キーの接頭語（処理の場合：タプルであるとき）

prcfrm = "frm" # 動的コード：モジュール＋クラス＋メソッド
prcarg = "arg" # 動的コード：引数群：優先順位（１）：ラベルからデータを取得するもの
prccnf = "cnf" # 動的コード：引数群：優先順位（２）：ラベルのみ取得するもの
prcsyn = "syn" # 動的コード：同期／非同期（同期＝True）

adrini = "/ini" # ルート：初期
adrset = "/set" # ルート：格納（内容から、内容キーを返却）
adrget = "/get" # ルート：取得（内容キーから、内容を返却）
adrsps = "/sps" # ルート：格納：ローデータを受け取り（受信完了を通知）
adrspp = "/spp" # ルート：格納：データキーを引き渡し（準備ができたら）
adrgps = "/gps" # ルート：取得：データキーを受け取り（受信完了を通知）
adrgpp = "/gpp" # ルート：取得：ローデータを引き渡し（準備ができたら）
adrprc = "/prc" # ルート：処理

#---------------------------------------------------------------------------
# 実行

appweb = web.Application()

appweb.add_routes([web.post(adrini, resini)])
appweb.add_routes([web.post(adrset, resset)])
appweb.add_routes([web.post(adrget, resget)])
appweb.add_routes([web.post(adrprc, resprc)])
appweb.add_routes([web.options(adrini, optpre)])
appweb.add_routes([web.options(adrset, optpre)])
appweb.add_routes([web.options(adrget, optpre)])
appweb.add_routes([web.options(adrprc, optpre)])

for i in range(numset):
  keyset = f"{i:03}"
  appweb.add_routes([web.post(adrsps + keyset, ressps)])
  appweb.add_routes([web.post(adrspp + keyset, resspp)])
  appweb.add_routes([web.options(adrsps + keyset, optpre)])
  appweb.add_routes([web.options(adrspp + keyset, optpre)])
  evtset[keyset] = asyncio.Event() # EVT
  evtset[keyset].clear() # EVT
  lstset[keyset] = []

for i in range(numget):
  keyget = f"{i:03}"
  appweb.add_routes([web.post(adrgps + keyget, resgps)])
  appweb.add_routes([web.post(adrgpp + keyget, resgpp)])
  appweb.add_routes([web.get(adrgpp + keyget, resgpp)]) # マイコンへの対応
  appweb.add_routes([web.options(adrgps + keyget, optpre)])
  appweb.add_routes([web.options(adrgpp + keyget, optpre)])
  evtget[keyget] = asyncio.Event() # EVT
  evtget[keyget].clear() # EVT
  lstget[keyget] = []

if secure == "0":
  web.run_app(appweb, port=svport)
if secure == "1":
  import ssl
  sslcon = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
  sslcon.load_cert_chain(dicnet["pthcrt"], dicnet["pthkey"])
  web.run_app(appweb, port=svport, ssl_context=sslcon)
