import pathlib
import libWiiPy

def nus_title_download(tid, version=None, output=None, wad=None, wii=False, endpoint=None, verbose=True):
    title_version = None
    wad_file = None
    output_dir = None
    can_decrypt = False
    wiiu_nus_enabled = False if wii else True
    endpoint_override = endpoint if endpoint else None

    # Check if version was passed, because it'll be None if it wasn't.
    if version is not None:
        try:
            title_version = int(version)
        except ValueError:
            if verbose:
                print("The specified Title Version must be a valid integer!")

    # If wad was passed, check to make sure the path is okay.
    if wad is not None:
        wad_file = pathlib.Path(wad)
        if wad_file.suffix != ".wad":
            wad_file = wad_file.with_suffix(".wad")

    # If output was passed, make sure the directory either doesn't exist or is empty.
    if output is not None:
        output_dir = pathlib.Path(output)
        if output_dir.exists():
            if output_dir.is_file():
                if verbose:
                    print("A file already exists with the provided directory name!")
        else:
            output_dir.mkdir()

    # Download the title from the NUS. This is done "manually" (as opposed to using download_title()) so that we can
    # provide verbose output.
    title = libWiiPy.title.Title()

    # Announce the title being downloaded, and the version if applicable.
    if verbose:
        if title_version is not None:
            print(f"Downloading title {tid} v{title_version}, please wait...")
        else:
            print(f"Downloading title {tid} vLatest, please wait...")
        print(" - Downloading and parsing TMD...")
    # Download a specific TMD version if a version was specified, otherwise just download the latest TMD.
    if title_version is not None:
        title.load_tmd(libWiiPy.title.download_tmd(tid, title_version, wiiu_endpoint=wiiu_nus_enabled,
                                                   endpoint_override=endpoint_override))
    else:
        title.load_tmd(libWiiPy.title.download_tmd(tid, wiiu_endpoint=wiiu_nus_enabled,
                                                   endpoint_override=endpoint_override))
        title_version = title.tmd.title_version
    # Write out the TMD to a file.
    if output_dir is not None:
        output_dir.joinpath(f"tmd.{title_version}").write_bytes(title.tmd.dump())

    # Download the ticket, if we can.
    if verbose:
        print(" - Downloading and parsing Ticket...")
    try:
        title.load_ticket(libWiiPy.title.download_ticket(tid, wiiu_endpoint=wiiu_nus_enabled,
                                                         endpoint_override=endpoint_override))
        can_decrypt = True
        if output_dir is not None:
            output_dir.joinpath("tik").write_bytes(title.ticket.dump())
    except ValueError:
        # If libWiiPy returns an error, then no ticket is available. Log this, and disable options requiring a
        # ticket so that they aren't attempted later.
        if verbose:
            print("  - No Ticket is available!")
        if wad_file is not None and output_dir is None:
            if verbose:
                print("--wad was passed, but this title has no common ticket and cannot be packed into a WAD!")

    # Load the content records from the TMD, and begin iterating over the records.
    title.load_content_records()
    content_list = []
    for content in range(len(title.tmd.content_records)):
        # Generate the content file name by converting the Content ID to hex and then removing the 0x.
        content_file_name = hex(title.tmd.content_records[content].content_id)[2:]
        while len(content_file_name) < 8:
            content_file_name = "0" + content_file_name
        if verbose:
            print(f" - Downloading content {content + 1} of {len(title.tmd.content_records)} "
                  f"(Content ID: {title.tmd.content_records[content].content_id}, "
                  f"Size: {title.tmd.content_records[content].content_size} bytes)...")
        content_list.append(libWiiPy.title.download_content(tid, title.tmd.content_records[content].content_id,
                                                            wiiu_endpoint=wiiu_nus_enabled,
                                                            endpoint_override=endpoint_override))
        if verbose:
            print("   - Done!")
        # If we're supposed to be outputting to a folder, then write these files out.
        if output_dir is not None:
            output_dir.joinpath(content_file_name).write_bytes(content_list[content])
    title.content.content_list = content_list

    # Try to decrypt the contents for this title if a ticket was available.
    if output_dir is not None:
        if can_decrypt is True:
            for content in range(len(title.tmd.content_records)):
                if verbose:
                    print(f" - Decrypting content {content + 1} of {len(title.tmd.content_records)} "
                          f"(Content ID: {title.tmd.content_records[content].content_id})...")
                dec_content = title.get_content_by_index(content)
                content_file_name = f"{title.tmd.content_records[content].content_id:08X}".lower() + ".app"
                output_dir.joinpath(content_file_name).write_bytes(dec_content)
        else:
            if verbose:
                print("Title has no Ticket, so content will not be decrypted!")

    # If wad was passed, pack a WAD and output that.
    if wad_file is not None:
        # Get the WAD certificate chain.
        if verbose:
            print(" - Building certificate...")
        title.load_cert_chain(libWiiPy.title.download_cert_chain(wiiu_endpoint=wiiu_nus_enabled,
                                                                 endpoint_override=endpoint_override))
        # Ensure that the path ends in .wad, and add that if it doesn't.
        if verbose:
            print("Packing WAD...")
        if wad_file.suffix != ".wad":
            wad_file = wad_file.with_suffix(".wad")
        # Have libWiiPy dump the WAD, and write that data out.
        pathlib.Path(wad_file).write_bytes(title.dump_wad())

    if verbose:
        print(f"Downloaded title with Title ID \"{tid}\"!")

# async def build_cios(entry, output_path, base_wad_path):
#     if os.path.exists(output_path):
#         try:
#             await verify_file(output_path, entry.md5, entry.md5alt)
#             return f"WAD {entry.wadname} found in cache"
#         except Exception:
#             print('NUS: Cached file verification failed, re-downloading')
#     if not entry.ciosslot or not entry.ciosversion:
#         raise CustomError(f"Missing cIOS slot or version for {entry.wadname}")
#     if not os.path.exists(base_wad_path):
#         raise CustomError(f"Base WAD file not found: {base_wad_path}")
#     d2x_modules = f"{MODMII_PATH}/Support/d2xModules"
#     cios_map_path = f"{d2x_modules}/ciosmaps.xml"
#     cios_version = entry.wadname[12:].replace('.wad', '')
#     args = [
#         "cios",
#         "--cios-ver", cios_version,
#         "--modules", d2x_modules,
#         "--slot", str(entry.ciosslot),
#         "--version", str(entry.ciosversion),
#         base_wad_path,
#         cios_map_path,
#         output_path
#     ]
#     return await run_command(args, entry.wadname, True)

# async def patch_ios(entry, output_path, base_wad_path):
#     if os.path.exists(output_path):
#         try:
#             await verify_file(output_path, entry.md5, entry.md5alt)
#             return f"WAD {entry.wadname} found in cache"
#         except Exception:
#             print('NUS: Cached file verification failed, re-downloading')
#     if not entry.ciosslot or not entry.ciosversion:
#         raise CustomError(f"Missing cIOS slot or version for {entry.wadname}")
#     if not os.path.exists(base_wad_path):
#         raise CustomError(f"Base WAD file not found: {base_wad_path}")
#     tmp_output_path = output_path.replace('(', '').replace(')', '')
#     args = [
#         "iospatch", "-fs", "-ei", "-na", "-vd", "-s", str(entry.ciosslot),
#         "-v", str(entry.ciosversion), base_wad_path, "-o", tmp_output_path
#     ]
#     await run_command(args, entry.wadname, True)
#     copy_file(tmp_output_path, output_path)
#     return None
