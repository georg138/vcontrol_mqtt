cmd_file = open("command_definition")
config_file = open("vito.xml", "w")
vclient_file = open("commands", "w")

config_file.write(
'''<?xml version="1.0"?>
<vito>
  <devices>
    <device ID="2020" name="WO1C" protocol="P300"/>
  </devices>
  <commands>
''')


for line in cmd_file:
    if line.lstrip().startswith("#") or line.isspace():
        continue
    else:
        cmd = line.split()
        # Name                 Adresse Typ Einheit rw
        name = cmd[0]
        address = cmd[1]
        type = cmd[2]
        unit = cmd[3]
        rw = cmd[4]
        description = cmd[5] if len(cmd) > 5 else name

        for access in rw:
            if access == "r":
                prefix = "get"
                protocmd = "getaddr"
                vclient_file.write(f'{prefix}{name}\n')
            elif access == "w":
                prefix = "set"
                protocmd = "setaddr"
            length = { "short": 2, "byte": 1, "bool" : 1 }[type]
            config_file.write(f'    <command name="{prefix}{name}" protocmd="{protocmd}">\n')
            config_file.write(f'      <addr>{address}</addr>\n')
            config_file.write(f'      <len>{length}</len>\n')
            config_file.write(f'      <description>{name}</description>\n')
            config_file.write(f'    </command>\n')

config_file.write(
'''  </commands>
</vito>
''')
