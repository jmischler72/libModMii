import hashlib
import pathlib
import binascii
from modules.core import fatal_error

def handle_nus_content(tid, cid, version=None, decrypt=False, output=None):

    # Only accepting the 000000xx format because it's the one that would be most commonly known, rather than using the
    # actual integer that the hex Content ID translates to.
    content_id = None
    try:
        content_id = int.from_bytes(binascii.unhexlify(cid))
    except binascii.Error:
        fatal_error("The provided Content ID is invalid! The Content ID must be in the format \"000000xx\"!")

    # Use the supplied output path if one was specified, otherwise generate one using the Content ID.
    if output is None:
        content_file_name = f"{content_id:08X}".lower()
        output_path = pathlib.Path(content_file_name)
    else:
        output_path = pathlib.Path(output)

    # Ensure that a version was supplied before downloading, because we need the matching TMD for decryption to work.
    if decrypt is True and version is None:
        fatal_error("You must specify the version that the requested content belongs to for decryption!")

    # Try to download the content, and catch the ValueError libWiiPy will throw if it can't be found.
    print(f"Downloading content with Content ID {cid}...")
    content_data = None
    try:
        content_data = libWiiPy.title.download_content(tid, content_id)
    except ValueError:
        fatal_error("The specified Title ID or Content ID could not be found!")

    if decrypt_content is True:
        output_path = output_path.with_suffix(".app")
        tmd = libWiiPy.title.TMD()
        tmd.load(libWiiPy.title.download_tmd(tid, version))
        # Try to get a Ticket for the title, if a common one is available.
        ticket = None
        try:
            ticket = libWiiPy.title.Ticket()
            ticket.load(libWiiPy.title.download_ticket(tid, wiiu_endpoint=True))
        except ValueError:
            fatal_error("No Ticket is available! Content cannot be decrypted.")

        content_hash = 'gggggggggggggggggggggggggggggggggggggggg'
        content_size = 0
        content_index = 0
        for record in tmd.content_records:
            if record.content_id == content_id:
                content_hash = record.content_hash.decode()
                content_size = record.content_size
                content_index = record.index

        # If the default hash never changed, then a content record matching the downloaded content couldn't be found,
        # which most likely means that the wrong version was specified.
        if content_hash == 'gggggggggggggggggggggggggggggggggggggggg':
            fatal_error("Content was not found in the TMD for the specified version! Content cannot be decrypted.")

        # Manually decrypt the content and verify its hash, which is what libWiiPy's get_content() methods do. We just
        # can't really use that here because that require setting up a lot more of the title than is necessary.
        content_dec = libWiiPy.title.decrypt_content(content_data, ticket.get_title_key(), content_index, content_size)
        content_dec_hash = hashlib.sha1(content_dec).hexdigest()
        if content_hash != content_dec_hash:
            fatal_error("The decrypted content provided does not match the record at the provided index. \n"
                        "Expected hash is: {}\n".format(content_hash) +
                        "Actual hash is: {}".format(content_dec_hash))
        output_path.write_bytes(content_dec)
    else:
        output_path.write_bytes(content_data)

    print(f"Downloaded content with Content ID \"{cid}\"!")

