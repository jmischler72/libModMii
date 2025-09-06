# "commands/title/ciosbuild.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import io
import os
import xml.etree.ElementTree as ET
import pathlib
import libWiiPy

def build_cios(
    base,
    map,
    cios_ver,
    modules=None,
    output=None,
    slot=None,
    version=None
):
    base_path = pathlib.Path(base)
    map_path = pathlib.Path(map)
    if modules:
        modules_path = pathlib.Path(modules)
    else:
        modules_path = pathlib.Path(os.getcwd())
    output_path = pathlib.Path(output)

    if not base_path.exists():
        print(f"The specified base IOS file \"{base_path}\" does not exist!")
    if not map_path.exists():
        print(f"The specified cIOS map file \"{map_path}\" does not exist!")
    if not modules_path.exists():
        print(f"The specified cIOS modules directory \"{modules_path}\" does not exist!")

    title = libWiiPy.title.Title()
    title.load_wad(open(base_path, 'rb').read())

    cios_tree = ET.parse(map_path)
    cios_root = cios_tree.getroot()

    target_cios = None
    for child in cios_root:
        cios = child.get("name")
        if cios_ver == cios:
            target_cios = child
            break
    if target_cios is None:
        print(f"The target cIOS \"{cios_ver}\" could not be found in the provided map!")

    target_base = None
    provided_base = int(title.tmd.title_id[-2:], 16)
    for child in target_cios:
        base_val = int(child.get("ios"))
        if base_val == provided_base:
            target_base = child
            break
    if target_base is None:
        print(f"The provided base (IOS{provided_base}) doesn't match any bases found in the provided map!")
    base_version = int(target_base.get("version"))
    if title.tmd.title_version != base_version:
        print(f"The provided base (IOS{provided_base} v{title.tmd.title_version}) doesn't match the required "
                    f"version (v{base_version})!")
    print(f"Building cIOS \"{cios_ver}\" from base IOS{target_base.get('ios')} v{base_version}...")

    print("Patching existing modules...")
    for content in target_base.findall("content"):
        patches = content.findall("patch")
        if patches:
            cid = int(content.get("id"), 16)
            dec_content = title.get_content_by_cid(cid)
            content_index = title.content.get_index_from_cid(cid)
            with io.BytesIO(dec_content) as content_data:
                for patch in patches:
                    offset = int(patch.get("offset"), 16)
                    original_data = b''
                    original_data_map = patch.get("originalbytes").split(",")
                    for byte in original_data_map:
                        original_data += bytes.fromhex(byte[2:])
                    new_data = b''
                    new_data_map = patch.get("newbytes").split(",")
                    for byte in new_data_map:
                        new_data += bytes.fromhex(byte[2:])
                    if original_data in dec_content:
                        content_data.seek(offset)
                        content_data.write(new_data)
                    else:
                        print("An error occurred while patching! Please make sure your base IOS is valid.")
                content_data.seek(0x0)
                dec_content = content_data.read()
            title.set_content(dec_content, content_index, content_type=libWiiPy.title.ContentType.NORMAL)

    print("Adding required additional modules...")
    for content in target_base.findall("content"):
        target_module = content.get("module")
        if target_module is not None:
            target_index = int(content.get("tmdmoduleid"), 16)
            cid = int(content.get("id"), 16)
            target_path = modules_path.joinpath(target_module + ".app")
            if not target_path.exists():
                print(f"A required module \"{target_module}\" could not be found!")
            new_module = target_path.read_bytes()
            if target_index == -1:
                title.add_content(new_module, cid, libWiiPy.title.ContentType.NORMAL)
            else:
                existing_module = title.get_content_by_index(target_index)
                existing_cid = title.content.content_records[target_index].content_id
                existing_type = title.content.content_records[target_index].content_type
                title.set_content(new_module, target_index, cid, libWiiPy.title.ContentType.NORMAL)
                title.add_content(existing_module, existing_cid, existing_type)

    if 3 <= slot <= 255:
        tid = title.tmd.title_id[:-2] + f"{slot:02X}"
        title.set_title_id(tid)
    else:
        print(f"The specified slot \"{slot}\" is not valid!")
    try:
        title.set_title_version(version)
    except ValueError:
        print(f"The specified version \"{version}\" is not valid!")
    print(f"Set cIOS slot to \"{slot}\" and cIOS version to \"{version}\"!")

    title_key_dec = title.ticket.get_title_key()
    title_key_common = libWiiPy.title.encrypt_title_key(title_key_dec, 0, title.tmd.title_id)
    title.ticket.title_key_enc = title_key_common
    title.ticket.common_key_index = 0

    title.fakesign()

    output_path.write_bytes(title.dump_wad())

    print(f"Successfully built cIOS \"{cios_ver}\"!")
