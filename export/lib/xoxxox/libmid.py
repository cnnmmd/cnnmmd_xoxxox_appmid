class LibMid:
  dicprc = {} # 処理の内容 # LibMid.dicprc["X"] = {"frm": "X.X.X", "arg": [...], "cnf": [...], "mem": [...], "syn": (True|False)}
  plugin = {} # プラグイン
  values = {} # 内容の格納（ターンごとに内容を消去する）
  memory = {} # 内容の格納（ターンごとに内容を消去せず）
