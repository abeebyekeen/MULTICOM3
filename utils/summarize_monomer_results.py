import os, sys, argparse, time
from multiprocessing import Pool
from tqdm import tqdm
import numpy as np
import pandas as pd
import pickle
from scipy.stats import pearsonr
from bml_casp15.common.util import check_file, check_dir, check_dirs, makedir_if_not_exists, check_contents, \
    read_option_file, is_file, is_dir


def cal_tmscore(tmscore_program, inpdb, nativepdb, tmpdir):
    cwd = os.getcwd()

    makedir_if_not_exists(tmpdir)

    os.chdir(tmpdir)

    os.system(f"cp {inpdb} inpdb.pdb")
    os.system(f"cp {nativepdb} native.pdb")

    inpdb = "inpdb.pdb"
    nativepdb = "native.pdb"

    cmd = tmscore_program + ' ' + inpdb + ' ' + nativepdb + " | grep TM-score | awk '{print $3}' "
    # print(cmd)
    tmscore_contents = os.popen(cmd).read().split('\n')
    tmscore = float(tmscore_contents[2].rstrip('\n'))
    cmd = tmscore_program + ' ' + inpdb + ' ' + nativepdb + " | grep GDT-score | awk '{print $3}' "
    tmscore_contents = os.popen(cmd).read().split('\n')
    gdtscore = float(tmscore_contents[0].rstrip('\n'))

    os.chdir(cwd)

    os.system("rm -rf " + tmpdir)

    return tmscore, gdtscore


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--option_file', type=is_file, required=True)
    parser.add_argument('--workdir', type=is_file, required=True)
    parser.add_argument('--tmpdir', type=str, required=True)

    args = parser.parse_args()

    makedir_if_not_exists(args.tmpdir)

    params = read_option_file(args.option_file)

    qa_dir = args.workdir + '/N4_monomer_structure_evaluation'

    if os.path.exists(args.workdir + '/N6_monomer_structure_evaluation'):
        print("Using img alignment in the pipeline")
        qa_dir = args.workdir + '/N6_monomer_structure_evaluation'

    if not os.path.exists(qa_dir):
        print("Rerunning the evaluation pipeline")
        qa_dir = args.workdir + '/N1_monomer_structure_evaluation'

    all_models = []
    all_alignments = []

    egnn_ranking = qa_dir + '/egnn_selected.csv'
    alignment_depth = []
    pairwise_ranking_df = pd.read_csv(egnn_ranking)
    ranked_modeles = []
    for i in range(len(pairwise_ranking_df)):
        model = pairwise_ranking_df.loc[i, 'selected_models']
        msa = qa_dir + '/msa/' + pairwise_ranking_df.loc[i, 'model'].replace('.pdb', '.a3m')
        alignment_depth += [len(open(msa).readlines())/2]
        ranked_modeles += [model]

    print(f"\negnn models: {ranked_modeles}, {alignment_depth}\n")
    all_models += ranked_modeles
    all_alignments += alignment_depth

    refine_dir = args.workdir + '/N5_monomer_structure_refinement_avg_final/'
    if os.path.exists(args.workdir + '/N7_monomer_structure_refinement_avg_final/'):
        refine_dir = args.workdir + '/N7_monomer_structure_refinement_avg_final/'

    if not os.path.exists(refine_dir):
        print("Rerunning the evaluation pipeline")
        refine_dir = args.workdir + '/N2_monomer_structure_refinement_avg_final/'

    refine_ranking = refine_dir + 'refine_selected.csv'
    refine_ranking_df = pd.read_csv(refine_ranking)
    ranked_modeles = []
    alignment_depth = []
    for i in range(5):
        ranked_modeles += [refine_ranking_df.loc[i, 'selected_models']]
        msa = refine_dir + '/' + refine_ranking_df.loc[i, 'model'].replace('.pdb', '.a3m')
        alignment_depth += [len(open(msa).readlines()) / 2]

    print(f"\nrefine models: {ranked_modeles}\n")
    all_models += ranked_modeles
    all_alignments += alignment_depth

    refine_dir = args.workdir + '/N5_monomer_structure_refinement_avg_final/'
    if os.path.exists(args.workdir + '/N7_monomer_structure_refinement_avg_final/'):
        refine_dir = args.workdir + '/N7_monomer_structure_refinement_avg_final/'

    if not os.path.exists(refine_dir):
        print("Rerunning the evaluation pipeline")
        refine_dir = args.workdir + '/N2_monomer_structure_refinement_avg_final/'

    refine_ranking = refine_dir + 'refine_selected.csv'
    refine_ranking_df = pd.read_csv(refine_ranking)
    ranked_modeles = []
    alignment_depth = []
    for i in range(5):
        ranked_modeles += [refine_ranking_df.loc[i, 'selected_models']]
        msa = refine_dir + '/' + refine_ranking_df.loc[i, 'model'].replace('.pdb', '.a3m')
        alignment_depth += [len(open(msa).readlines()) / 2]

    deep_ranking = qa_dir + '/deep_selected.csv'
    alignment_depth = []
    pairwise_ranking_df = pd.read_csv(deep_ranking)
    ranked_modeles = []
    for i in range(len(pairwise_ranking_df)):
        model = pairwise_ranking_df.loc[i, 'selected_models']
        msa = qa_dir + '/msa/' + pairwise_ranking_df.loc[i, 'model'].replace('.pdb', '.a3m')
        alignment_depth += [len(open(msa).readlines()) / 2]
        ranked_modeles += [model]

    print(f"\ndeep models: {ranked_modeles}, {alignment_depth}\n")
    all_models += ranked_modeles
    all_alignments += alignment_depth

    refine_qa_dir = args.workdir + '/N5_monomer_structure_refinement_af_final/'
    qa_ranking = refine_qa_dir + 'qa_selected.csv'
    qa_ranking_df = pd.read_csv(qa_ranking)
    ranked_modeles = []
    alignment_depth = []
    for i in range(5):
        ranked_modeles += [qa_ranking_df.loc[i, 'selected_models']]
        msa = refine_qa_dir + '/' + qa_ranking_df.loc[i, 'model'].replace('.pdb', '.a3m')
        alignment_depth += [len(open(msa).readlines()) / 2]
    print(f"\nqa models: {ranked_modeles}\n")
    all_models += ranked_modeles
    all_alignments += alignment_depth

    df = pd.DataFrame({'model': all_models, 'alignment_depth': all_alignments})
    print(df)
    df.to_csv(args.workdir + '/summary.csv')

    pdb70_hit_file = args.workdir + '/N3_monomer_structure_generation/default/msas/pdb_hits.hhr'
    if os.path.exists(pdb70_hit_file):
        start = False
        contents = open(pdb70_hit_file).readlines()
        for i, line in enumerate(contents):
            line = line.rstrip('\n')
            if line == "No 1":
                template_name = contents[i+1].split()[0].lstrip('>')
                evalue = contents[i+2].split()[1].split('=')[1]
                print(f"\nPDB70 Template: {template_name}, e-value: {evalue}")
                break

    pdb_hit_file = args.workdir + '/N2_monomer_template_search/output.hhr'
    if os.path.exists(pdb_hit_file):
        start = False
        contents = open(pdb_hit_file).readlines()
        for i, line in enumerate(contents):
            line = line.rstrip('\n')
            if line == "No 1":
                template_name = contents[i + 1].split()[0].lstrip('>')
                evalue = contents[i + 2].split()[1].split('=')[1]
                print(f"\nIn house PDB Template: {template_name}, e-value: {evalue}")
                break
