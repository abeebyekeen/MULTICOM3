###################################################################
#Script to generate dimers' msas using interaction calculated from RCSB_PDB
#Dependency: dimer's relation generated from RCSB_PDB
###################################################################

import os, sys, argparse, time, ftplib
from util import is_dir, is_file, read_option_file, check_dirs, check_contents, die, makedir_if_not_exists, clean_dir, cal_sequence_identity_from_seq
from multiprocessing import Pool
from collections import OrderedDict
import re
import pandas as pd
from alignment import read_fasta, read_a3m, write_a3m, clean_a3m
from complex import write_concatenated_alignment


def get_interaction_from_string(dimers_relation_map_from_string, alignment_1, alignment_2, chain1, chain2):

    # load the monomer alignments
    ali_1 = read_a3m(alignment_1, True)

    ali_2 = read_a3m(alignment_2, True)

    id_1 = []
    id_2 = []

    for id1 in ali_1:

        if id1 not in dimers_relation_map_from_string:

            continue

        interact_ids = dimers_relation_map_from_string[id1]

        for id2 in ali_2:
            
            if id2 in interact_ids.split(','):

                id_1 += [id1]

                id_2 += [id2]

    return pd.DataFrame(
        {"id_1": id_1, "id_2": id_2}
    ) 


def generate_alignments_for_heterodimers(inparams):

    dimers_relation_map_from_string, chain1, chain2, monomers_msa_dir, outdir = inparams

    chain1_a3m = monomers_msa_dir + '/' + chain1 + '.a3m'
    chain2_a3m = monomers_msa_dir + '/' + chain2 + '.a3m'

    if not os.path.exists(chain1_a3m):
        #die(f"Cannot find a3m file for {chain1}: {chain1_a3m}\n")
        return

    if not os.path.exists(chain2_a3m):
        #die(f"Cannot find a3m file for {chain2}: {chain2_a3m}\n")
        return

    print(f"Processing {chain1}_{chain2}")
    outdir = f"{outdir}/{chain1}_{chain2}"
    makedir_if_not_exists(outdir)

    makedir_if_not_exists(outdir + '/' + chain1)
    clean_a3m(chain1_a3m, outdir + '/' + chain1 + '/' + chain1 + '.a3m')

    makedir_if_not_exists(outdir + '/' + chain2)
    clean_a3m(chain2_a3m, outdir + '/' + chain2 + '/' + chain2 + '.a3m')

    chain1_a3m = outdir + '/' + chain1 + '/' + chain1 + '.a3m'
    chain2_a3m = outdir + '/' + chain2 + '/' + chain2 + '.a3m'

    dimers_interaction = get_interaction_from_string(dimers_relation_map_from_string, chain1_a3m, chain2_a3m, chain1, chain2)

    # write concatenated alignment with distance filtering
    # TODO: save monomer alignments?
    target_header, target_seq_idx, sequences_full, sequences_monomer_1, sequences_monomer_2 = \
        write_concatenated_alignment(dimers_interaction, chain1_a3m, chain2_a3m, chain1, chain2)

    # save the alignment files
    mon_alignment_file_1 = f"{outdir}/{chain1}/{chain1}_monomer_1.a3m"
    with open(mon_alignment_file_1, "w") as of:
        write_a3m(sequences_monomer_1, of)

    mon_alignment_file_2 = f"{outdir}/{chain2}/{chain2}_monomer_2.a3m"
    with open(mon_alignment_file_2, "w") as of:
        write_a3m(sequences_monomer_2, of)

    dimers_interaction.to_csv(f"{outdir}/{chain1}_{chain2}_interact.csv", index=False)

    complex_ailgnment_file = f"{outdir}/{chain1}_{chain2}.a3m"
    with open(complex_ailgnment_file, "w") as of:
        write_a3m(sequences_full, of)


def test(params):

    threshold = 0
    dimers_relation_map_from_string = {}

    print("Reading maps")
    with open(params['string2uniprot_map']) as f:
        for line in f:
            uniprotid1, uniprotid2, score = line.rstrip('\n').split()

            if int(score) < threshold:
                continue

            if uniprotid1 in dimers_relation_map_from_string:
                dimers_relation_map_from_string[uniprotid1] += "," + uniprotid2
            else:
                dimers_relation_map_from_string[uniprotid1] = uniprotid2

            if uniprotid2 in dimers_relation_map_from_string:
                dimers_relation_map_from_string[uniprotid2] += "," + uniprotid1
            else:
                dimers_relation_map_from_string[uniprotid2] = uniprotid1

    print("Generating alignments")
    generate_alignments_for_heterodimers([dimers_relation_map_from_string, '1A5XA', '1A62A', '/home/jl4mc/multicom4s/multicom4s/tool/update_complex_dbs/a3m'])

    die("111111111")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--option_file', type=is_file, required=True)
    args = parser.parse_args()

    t1 = time.time()

    params = read_option_file(args.option_file)

    abs_opt = os.path.abspath(args.option_file)

    # test(params)

    check_dirs(params, ['prosys_dir', 'complex_set_work_dir'])

    check_contents(params, ['monomers_cm_database_name', 'monomers_in_complex_database_name', 'monomers_not_in_complex_database_name'])

    original_work_dir = params['complex_set_work_dir'] + '/original'

    current_work_dir = params['complex_set_work_dir']

    # generate msas for heterodimers

    os.system(f"cp {original_work_dir}/heterodimers.list {current_work_dir}")

    heterodimers_list = f"{current_work_dir}/heterodimers.list"

    threshold = 0
    dimers_relation_map_from_string = {}

    print("Reading maps")
    with open(params['string2uniprot_map']) as f:
        for line in f:
            uniprotid1, uniprotid2, score = line.rstrip('\n').split()

            if int(score) < threshold:
                continue

            if uniprotid1 in dimers_relation_map_from_string:
                dimers_relation_map_from_string[uniprotid1] += "," + uniprotid2
            else:
                dimers_relation_map_from_string[uniprotid1] = uniprotid2

            if uniprotid2 in dimers_relation_map_from_string:
                dimers_relation_map_from_string[uniprotid2] += "," + uniprotid1
            else:
                dimers_relation_map_from_string[uniprotid2] = uniprotid1


    contents = open(heterodimers_list, "r").readlines()

    makedir_if_not_exists(current_work_dir + '/fr_dimers/string')

    for content in contents:

        content = content.replace('\n', '').replace('\r', '')

        pdbcode, chain1, chain2 = content.split()

        generate_alignments_for_heterodimers([dimers_relation_map_from_string, chain1, chain2,
                                              current_work_dir + '/fr',
                                              current_work_dir + '/fr_dimers/string'])

    t2 = time.time()

    print("Fr library updating is done. Total time:" + (t2 - t1).__str__())
