import os
import os.path
import sys
import argparse
import glob
import helper

from model import Model
from note import *

def main():
	parser = argparse.ArgumentParser()

	parser.add_argument("-t",
		help = "Test files that were used to generate predictions",
		dest = "txt",
		default = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/test_data/*')
	)
	
	parser.add_argument("-c",
		help = "Predicted concepts",
		dest = "con",
		default = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/test_predictions/*')
	)

	parser.add_argument("-r",
		help = "Reference gold standard concepts",
		dest = "ref",
		default = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/reference_standard_for_test_data/concepts/*')
	)

	args = parser.parse_args()

	files = []
	txt_files = glob.glob(args.txt)
	con_files = glob.glob(args.con)
	ref_files = glob.glob(args.ref)

	txt_files_map = helper.map_files(txt_files)
	con_files_map = helper.map_files(con_files)
	ref_files_map = helper.map_files(ref_files)

	for k in txt_files_map:
		if k in con_files_map and k in ref_files_map:
			files.append((txt_files_map[k], con_files_map[k], ref_files_map[k]))
	


	# Locate the files
	#path = 'data/test_data'
	#txts = [os.path.join(path, f) for f in os.listdir(path)]
	#
	#path = 'data/test_predictions'
	#cons = [os.path.join(path, f) for f in os.listdir(path)]
	#name = lambda f: f.split(os.sep)[-1]
	#assert "files lined up", all(name(t)[:-3] == name(c)[:-3] for t, c in zip(txts, cons))
	#
	#path = 'data/reference_standard_for_test_data/concepts'
	#refs = [os.path.join(path, f) for f in os.listdir(path)]
	#assert "refs lined up", all(name(r) == name(c) for r, c in zip(refs, cons))
	#
	#files = zip(txts, cons, refs)
	


	# Compute the confusion matrix
	labels = Model.labels
	confusion = [[0] * len(labels) for e in labels]
	for txt, con, ref in files:
		txt = read_txt(txt)
		for c, r in zip(read_con(con, txt), read_con(ref, txt)):
			for c, r in zip(c, r):
				confusion[labels[r]][labels[c]] += 1
	


	# Display the confusion matrix
	print "Confusion Matrix"
	pad = max(len(l) for l in labels)
	print "%s %s" % (' ' * pad, "\t".join(Model.labels.keys()))
	for act, act_v in labels.items():
		print "%s %s" % (act.rjust(pad), "\t".join([str(confusion[act_v][pre_v]) for pre, pre_v in labels.items()]))
	print
	
	
	
	# Compute the analysis stuff
	precision = []
	recall = []
	specificity = []
	f1 = []

	print "Analysis"
	print " " * pad, "Precision\tRecall\tF1"

	for lab, lab_v in labels.items():
		tp = confusion[lab_v][lab_v]
		fp = sum(confusion[v][lab_v] for k, v in labels.items() if v != lab_v)
		fn = sum(confusion[lab_v][v] for k, v in labels.items() if v != lab_v)
		tn = sum(confusion[v1][v2] for k1, v1 in labels.items() 
			for k2, v2 in labels.items() if v1 != lab_v and v2 != lab_v)
		precision += [float(tp) / (tp + fp + 1e-100)]
		recall += [float(tp) / (tp + fn + 1e-100)]
		specificity += [float(tn) / (tn + fp + 1e-100)]
		f1 += [float(2 * tp) / (2 * tp + fp + fn + 1e-100)]
		print "%s %.4f\t%.4f\t%.4f" % (lab.rjust(pad), precision[-1], recall[-1], f1[-1])

	print "--------"

	precision = sum(precision) / len(precision)
	recall = sum(recall) / len(recall)
	specificity = sum(specificity) / len(specificity)
	f1 = sum(f1) / len(f1)

	print "Average: %.4f\t%.4f\t%.4f\t%.4f" % (precision, recall, specificity, f1)
	
if __name__ == '__main__':
	main()