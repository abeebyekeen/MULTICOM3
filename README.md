# MULTICOM3 
Note: Currently we are still organizing this software package. It is expected to be fully functional in three weeks.

MULTICOM3 is an addon package to improve AlphaFold2- and AlphaFold-Multimer-based predition of protein tertiary and quaternary structures by diverse multiple sequene alignment sampling, template identification, model evaluation and model refinement. In CASP15, MULTICOM3 used AlphaFold v2.2 as the engine to generate models. In this release, it is adjusted to run on top of AlphaFold v2.3 (https://github.com/deepmind/alphafold/releases/tag/v2.3.2) to leverage the latest improvement on AlphaFold2.

## Overall workflow
![CASP15 pipeline](imgs/pipeline.png)


# Installation

## Python virtual environment

Our system is built on top of AlphaFold2/AlphaFold-Multimer, please follow the installation guide here: https://github.com/kalininalab/alphafold_non_docker to install the required python packages to run AlphaFold2/AlphaFold-Multimer, then run the following commands to install the additional packages required in our system.

```
conda install tqdm

# install ColabFold
pip install "colabfold[alphafold] @ git+https://github.com/sokrypton/ColabFold"

```
## Download databases and tools in MULTICOM3

```
python setup.py
```

### Genetic databases

Assume the following databases have been installed as a part of the AlphaFold2/AlphaFold-Multimer
*   [BFD](https://bfd.mmseqs.com/),
*   [MGnify](https://www.ebi.ac.uk/metagenomics/),
*   [PDB70](http://wwwuser.gwdg.de/~compbiol/data/hhsuite/databases/hhsuite_dbs/),
*   [PDB](https://www.rcsb.org/) (structures in the mmCIF format),
*   [PDB seqres](https://www.rcsb.org/)
*   [UniRef30](https://uniclust.mmseqs.com/),
*   [UniProt](https://www.uniprot.org/uniprot/),
*   [UniRef90](https://www.uniprot.org/help/uniref).

Additional databases will be installed for the MULTICOM system:
*   [AlphaFoldDB](https://alphafold.ebi.ac.uk/),
*   [ColabFold database](https://colabfold.mmseqs.com/),
*   [Integrated Microbial Genomes (IMG)](https://img.jgi.doe.gov/),
*   [Metaclust](https://metaclust.mmseqs.org/current_release/),
*   [STRING](https://string-db.org/cgi/download?sessionId=bgV6D67b9gi2),
*   [pdb_complex](https://www.biorxiv.org/content/10.1101/2023.05.16.541055v1),
*   [pdb_sort90](https://www.biorxiv.org/content/10.1101/2023.05.01.538929v1),
*   [Uniclust30](https://uniclust.mmseqs.com/).


# Running the monomer/teritary structure prediction pipeline
```bash
python bin/monomer.py \
    --option_file bin/db_option \
    --fasta_path $YOUR_FASTA \
    --output_dir $OUTDIR
```
# Running the multimer/quaternary structure prediction pipeline
```bash
# For homo-multimer
# stoichiometry: A4
python bin/homomer.py \
    --option_file bin/db_option \
    --fasta_path $YOUR_FASTA \
    --stoichiometry $STOICHIOMETRY \ 
    --output_dir $OUTDIR

# For hetero-multimer
# stoichiometry: A1B1/A9B9C9
# stoichiometry2: heterodimer or heteromer
python bin/heteromer.py \
    --option_file bin/db_option \
    --fasta_path $YOUR_FASTA \
    --stoichiometry $STOICHIOMETRY \ 
    --stoichiometry2 $STOICHIOMETRY2 \ 
    --output_dir $OUTDIR
```

# Examples

## Folding a monomer

Say we have a monomer with the sequence `<SEQUENCE>`. The input fasta should be:

```fasta
>sequence_name
<SEQUENCE>
```

Then run the following command:

```bash
python bin/monomer.py \
    --option_file bin/db_option \
    --fasta_path monomer.fasta \
    --output_dir outdir
```

## Folding a homo-multimer

Say we have a homomer with 4 copies of the same sequence
`<SEQUENCE>`. The input fasta should be:

```fasta
>sequence_1
<SEQUENCE>
>sequence_2
<SEQUENCE>
>sequence_3
<SEQUENCE>
>sequence_4
<SEQUENCE>
```

Then run the following command:

```bash
python bin/homomer.py \
    --option_file bin/db_option \
    --fasta_path homomer.fasta \
    --stoichiometry A4 \ 
    --output_dir outdir
```

## Folding a hetero-multimer

Say we have an A2B3 heteromer, i.e. with 2 copies of
`<SEQUENCE A>` and 3 copies of `<SEQUENCE B>`. The input fasta should be:

```fasta
>sequence_1
<SEQUENCE A>
>sequence_2
<SEQUENCE A>
>sequence_3
<SEQUENCE B>
>sequence_4
<SEQUENCE B>
>sequence_5
<SEQUENCE B>
```

Then run the following command:

```bash
python bin/heteromer.py \
    --option_file bin/db_option \
    --fasta_path heteromer.fasta \
    --stoichiometry A2B3 \ 
    --stoichiometry2 heteromer \ 
    --output_dir outdir
```

## Output

### Monomer

* The models and ranking files are saved in *N5_monomer_structure_refinement_avg* folder. You can check the alphafold pLDDT score ranking file (alphafold_ranking.csv) to look for the structure with the highest pLDDT score. The *pairwise_ranking.tm* and *pairwise_af_avg.ranking* are the other two ranking files. 

* The refined monomer models are saved in *N5_monomer_structure_refinement_avg_final*.

### Multimer (Homo-multimer and hetero-multimer)

* The models and ranking files are saved in *N9_multimer_structure_evaluation*, similarly, you can check the alphafold confidence score ranking file (alphafold_ranking.csv) to look for the structure with the highest predicted confidence score generated by AlphaFold-Multimer. The *multieva.csv* and *pairwise_af_avg.ranking* are the other two ranking files.

* The refined multimer models are saved in *N10_multimer_structure_refinement_final*.

* The monomer structures and ranking files are saved in *N7_monomer_structure_evaluation* if you want to check the models and rankings for the monomer structures.

## Some CASP15 Prediction Examples

![CASP15 pipeline](imgs/CASP15_good_examples1.png)
![CASP15 pipeline](imgs/CASP15_good_examples2.png)


# Citing this work

**If you use the code or data in this package for tertiary or quaternary structure prediction, please cite:**

Jumper, J., Evans, R., Pritzel, A., Green, T., Figurnov, M., Ronneberger, O., ... & Hassabis, D. (2021). Highly accurate protein structure prediction with AlphaFold. Nature, 596(7873), 583-589.

Evans, R., O’Neill, M., Pritzel, A., Antropova, N., Senior, A., Green, T., ... & Hassabis, D. (2021). Protein complex prediction with AlphaFold-Multimer. BioRxiv, 2021-10.
 
Liu, J., Guo, Z., Wu, T., Roy, R. S., Chen, C., & Cheng, J. (2023). Improving AlphaFold2-based Protein Tertiary Structure Prediction with MULTICOM in CASP15. bioRxiv, 2023-05.

Liu, J., Guo, Z., Wu, T., Roy, R. S., Quadir, F., Chen, C., & Cheng, J. (2023). Enhancing AlphaFold-Multimer-based Protein Complex Structure Prediction with MULTICOM  in CASP15. bioRxiv, to be submitted. 



