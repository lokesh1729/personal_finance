import os
import re
import logging


def rename_it(dirpath, path_suffix, is_dir):
	pattern = r"([a-zA-Z0-9\s\+\&\']+)\s([a-z0-9]{32})"
	match = re.match(pattern, path_suffix)
	if match is not None:
		if is_dir:
			new_name = match.group(1)
		else:
			new_name = match.group(1) + ".md"
		os.rename(os.path.join(dirpath, path_suffix), os.path.join(dirpath, new_name))
		logger.info("Successfully renamed from %s to %s", os.path.join(dirpath, path_suffix), os.path.join(dirpath, new_name))
	else:
		logger.warn("Pattern did not match. Skipping %s", os.path.join(dirpath, path_suffix))



def main():
	rename_list = []
	for dirpath, dirnames, filenames in os.walk("/Users/lokeshsanapalli/Downloads/e2544a0d-34b2-4c2c-861e-e1f44e56f7d6_Export-5fe8eacd-fb00-42f8-a5cd-e34ec62c5c02", topdown=False):
		for each_file in filenames:
			rename_it(dirpath, each_file, False)
		for each_dirname in dirnames:
			rename_it(dirpath, each_dirname, True)


if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO)
	logger = logging.getLogger(__name__)
	main()
