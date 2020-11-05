import os
import subprocess


SIMPLESIM = "simplesim-3v0e/simplesim-3.0/"
CACHE = (("il1", "dl1"), ("dl1", "il1"))
BENCHMARKS = {
    "LI": "li.ss li.lsp",
    "VORTEX": "vortex.ss tiny.in"
}

# Experiment 1
ASSOC_1 = (1, 2, 4, 128)
ASSOC_2 = (1, 2, 4, 256)

# Experiment 2
REPL = ('l', 'f', 'r')


def get_misses(output, cache):
    for line in output.split('\n'):
        if "sim_num_insn" in line:
            _, instructions, *_ = line.split()

        if "sim_num_refs" in line:
            _, loads_stores, *_ = line.split()

        elif f"{cache}.misses" in line:
            _, misses, *_ = line.split()

        elif f"{cache}.miss_rate" in line:
            _, miss_rate, *_ = line.split()

        elif f"{cache}.replacements" in line:
            _, replacements, *_ = line.split()

    return instructions, loads_stores, misses, miss_rate, replacements


def first_experiment(total, assocs):
    for benchmark, benchmark_file in BENCHMARKS.items():
        for cache_experiment, cache in CACHE:
            for assoc in assocs:
                nsets = int(total / assoc)

                command = f"./sim-cache -cache:{cache_experiment} {cache_experiment}:{nsets}:64:{assoc}:l "\
                    + f"-cache:il2 none -cache:{cache} {cache}:64:64:1:l -cache:dl2 none -tlb:itlb none "\
                    + f"-tlb:dtlb none {benchmark_file}"

                output = subprocess.run(
                    command.split(), capture_output=True, text=True).stderr

                instructions, loads_stores, misses, miss_rate, *_ = get_misses(
                    output, cache_experiment)
                line = f"{benchmark},{cache_experiment},{instructions},{loads_stores},{nsets},{assoc},{misses},{miss_rate}\n"

                with open('../../first_experiment.csv', 'a') as output_file:
                    output_file.write(line)


if __name__ == "__main__":
    os.chdir(SIMPLESIM)

    with open('../../first_experiment.csv', 'w') as output_file:
        output_file.write(
            "Benchmark,Cache,instructions,Loads/Stores,nsets,assoc,misses,miss_rate\n")

    first_experiment(128, ASSOC_1)
    first_experiment(256, ASSOC_2)
