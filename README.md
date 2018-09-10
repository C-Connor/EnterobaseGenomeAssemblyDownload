# EnterobaseGenomeAssemblyDownload
A python script for automating download of genome assemblies in fasta format from [Enterobase](enterobase.warwick.ac.uk). Genomes of interest are specified using an input download list. A 5 second wait time is used between each download request.

An [Enterobase](enterobase.warwick.ac.uk) user log in with valid [API access](http://enterobase.readthedocs.io/en/latest/api/api-getting-started.html) is required to run this script. The script will prompt for a username and password for access to Enterobase, this is not the API token. The script will automatically retrieve the API token.

## Generating the download list.
Instructions for creating the download file from enterobase required by this script. These instructions can also be viewed using the the `--instructions` flag.

1. Go to enterobase.warwick.ac.uk and select your database of interest. Select 'Search strains'.
2. Search for your desired strains. Ensure that 'Ignore Legacy Strains' is checked.
3. Ensure that 'Experimental Data' in the top right corner, is set to 'Assembly Stats'.
4. Download the text file by selecting 'Data > Save to Local File'.
5. The resulting text file should contain columns corresponding to those on enterobase. There should also be a column called 'Assembly Barcode'.

## Input
This script requires a 'download list' which is to be generated following the instructions above. Please provide the path and name of the text file using the `-l` or `--download-list` flags.

The script also requires that the query database be specified with the flag `-d` or `--database`. The current options are: senterica, ecoli, yersinia or mcatarrhalis. Please specify only one.

## Output
The script will download the assemblies in fasta format and save them into the specified output directory. The assemblies will be named according to their assembly barcode on Enterobase. The script will also generate two log files: "assembly_code_error_log" and "fasta_error_log". The first contains details on assemblies which could not be identified on Enterobase (e.g. an incorrect assembly code) the second log contains details of which assemblies could not be downloaded (data embargo).
