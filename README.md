# EnterobaseGenomeAssemblyDownload
A python script for automating download of genome assemblies in fasta format from [Enterobase](enterobase.warwick.ac.uk). Genomes of interest are specified using an input download list. A 5 second wait time is used between each download request.

An [Enterobase](enterobase.warwick.ac.uk) user log in with valid [API access](http://enterobase.readthedocs.io/en/latest/api/api-getting-started.html) is required to run this script.

## Generating the download list.
Instructions for creating the download file from enterobase required by this script. These instructions can also be viewed using the the `--instructions` flag.

1. Go to enterobase.warwick.ac.uk and select your database of interest. Select 'Search strains'.
2. Search for your desired strains.
3. Ensure that 'Experimental Data' in the top right corner, is set to 'Assembly Stats'.
4. Download the text file by selecting 'Data > Save to Local File'.
5. The resulting text file should contain columns corresponding to those on enterobase. There should also be a column called 'Assembly Barcode'.
