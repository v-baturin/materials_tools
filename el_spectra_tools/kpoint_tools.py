from pathlib import Path
import re
import numpy as np
import os

def add_labels_to_0weigth_kpoint_file(kpoints_file: str | os.PathLike = 'KPOINTS',
                                      labelled_source: str | os.PathLike = 'KPOINTS_OPT') -> None:
    """
    Adds K-point labels from a Line-mode labelled KPOINTS file (labelled source) and use them to annotate the 0-weight
    K-points in the KPOINTS file. Useful for plotting of band structures from hybrid-functional calculations
    :param kpoints_file: KPOINTS-file to label
    :param label_source: source of labels (vaspkit-generated KPATH.in or KPOINTS_OPT file)
    :return: None
    """
    weighted_kp_line_pattern = r'^\s*([-+]?\d*\.?\d+\s+){3}\d+\s*$'
    with open(kpoints_file, 'r') as kp_fid, open(labelled_source, 'r') as klabel_src_fid:
        labels_source_dict = dict()
        for line in klabel_src_fid.readlines()[4:]:
            if line.strip():
                x, y, z, l = line.strip().split()
                l = '$\Gamma$' if l.casefold()[0] == 'g' else l
                labels_source_dict[tuple(float(i) for i in (x,y,z))] = l
        kpoints_lines_old = kp_fid.readlines()
        kpoints_lines_new = []
        for line in kpoints_lines_old:
            if re.match(weighted_kp_line_pattern, line.strip()):
                x, y, z, w = line.split(maxsplit=4)
                dict_key = tuple(float(i) for i in (x,y,z))
                if dict_key in labels_source_dict and w == '0':
                    kpoints_lines_new.append(line[:-1] + f' {labels_source_dict[dict_key]}' + '\n')
                    continue
            kpoints_lines_new.append(line)
    with open(kpoints_file, 'w') as kp_fid, open(kpoints_file.parent / kpoints_file.name + '_backup', 'w') as kp_bkp:
        kp_bkp.writelines(kpoints_lines_old)
        kp_fid.writelines(kpoints_lines_new)


if __name__ == '__main__':
    calc_fold = Path(os.getcwd())
    kp_source = calc_fold /'KPATH.in'
    kpoints = calc_fold / 'KPOINTS'
    add_labels_to_0weigth_kpoint_file(kpoints, kp_source)

