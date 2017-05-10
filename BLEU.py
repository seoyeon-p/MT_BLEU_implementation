import math
import os

candidate_path = "./HW8_TestSet/candidatelist"
reference_path = "./HW8_TestSet/referencelist"



def read_file(filename):
    f = open(filename, "r", encoding="utf-8")
    file = f.readlines()
    f.close()
    return file

def read_dir(candidate_path, reference_path):
    reference_list = []
    candidate_list = []
    if os.path.isfile(candidate_path):
        candidate_list.append(read_file(candidate_path))
    else:
        for f in os.listdir(candidate_path):
            candidate_list = read_file(f)

    if os.path.isfile(reference_path):
        reference_list.append(read_file(reference_path))
    else:
        for f in os.listdir(reference_path):
            reference_list.append(read_file(f))

    return candidate_list, reference_list

def modified_precision(candidate_dict, reference_dict):
    val = 0
    for m in candidate_dict.keys():
        m_w = candidate_dict[m]
        m_max = 0
        for ref in reference_dict:
            if m in ref:
                m_max = max(m_max, ref[m])
        m_w = min(m_w, m_max)
        val += m_w
    return val

def get_closest_ref_len(reference_len, candidate_len):
    closest = min(reference_len, key=lambda reference_len: (abs(reference_len - candidate_len),reference_len))
    return closest

def brevity_penalty(closest_value, reference_len):
    if closest_value > reference_len:
        return 1
    elif closest_value == 0:
        return 0
    else:
        return math.exp(1 - (float(reference_len) / closest_value))

def referecen_dict(references,n):
    reference_count, reference_len = [], []
    result = ""
    for ref in references:
        for i in range(0,len(ref)):
            sentence = ref[i]
            dict = {}
            words = sentence.strip().split()
            reference_len.append(len(words))
            max_val = len(words) - n + 1
            for j in range(0,len(max_val)):
                result += words[j:j+n].lower()
                if result in dict:
                    dict[result] += 1
                else:
                    dict[result] = 1
            reference_count.append(dict)


def ngram(candidate, references, n):
    clipped_count, count, reference_length, closest_val = 0, 0, 0, 0
    for i in range(0,len(candidate)):
        ref_counts = []
        ref_lengths = []
        for reference in references:
            ref_sentence = reference[i]
            ngram_d = {}

            words = ref_sentence.strip().split()
            ref_lengths.append(len(words))
            limits = len(words) - n + 1
            for j in range(limits):
                ngram = ' '.join(words[j:j + n]).lower()
                if ngram in ngram_d:
                    ngram_d[ngram] += 1
                else:
                    ngram_d[ngram] = 1
            ref_counts.append(ngram_d)

        cand_sentence = candidate[i]
        cand_dict = {}
        words = cand_sentence.strip().split()
        limits = len(words) - n + 1
        for j in range(0, limits):
            ngram = ' '.join(words[j:j + n]).lower()
            if ngram in cand_dict:
                cand_dict[ngram] += 1
            else:
                cand_dict[ngram] = 1
        clipped_count += modified_precision(cand_dict, ref_counts)
        count += limits
        reference_length += get_closest_ref_len(ref_lengths, len(words))
        closest_val += len(words)

    precision = float(clipped_count) / count
    penalty_val = brevity_penalty(closest_val, reference_length)
    return precision, penalty_val

def bleu(candidate, references):
    val = 1
    precisions = []
    for i in range(0,4):
        precision_val, brv_val = ngram(candidate, references, i + 1)
        precisions.append(precision_val)
    for i in range(0,len(precisions)):
        val *= float(precisions[i])
    val = math.pow(val,(1.0/len(precisions))) * brv_val
    return val


candidate, references = read_dir(candidate_path, reference_path)
val = bleu(candidate, references)
print(val)
foutput = open('bleu_out.txt', 'w')
foutput.write(str(val))
foutput.close()
