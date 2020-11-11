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

# Experiment 3
BSIZE = (16, 32, 64, 128)


def parse_output(output, cache):
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

                instructions, loads_stores, misses, miss_rate, *_ = parse_output(
                    output, cache_experiment)
                line = f"{benchmark},{cache_experiment},{instructions},{loads_stores},{nsets},{assoc},{misses},{miss_rate}\n"

                with open('../../Experiment-1.csv', 'a') as output_file:
                    output_file.write(line)


def second_experiment(repls):
    for benchmark, benchmark_file in BENCHMARKS.items():
        for cache_experiment, cache in CACHE:
            for repl in repls:
                command = f"./sim-cache -cache:{cache_experiment} {cache_experiment}:1:32:256:{repl} "\
                    + f"-cache:il2 none -cache:{cache} {cache}:1:32:256:l -cache:dl2 none -tlb:itlb none "\
                    + f"-tlb:dtlb none {benchmark_file}"

                output = subprocess.run(
                    command.split(), capture_output=True, text=True).stderr

                instructions, loads_stores, misses, miss_rate, replacements = parse_output(
                    output, cache_experiment)
                line = f"{benchmark},{cache_experiment},{instructions},{loads_stores},{repl},{misses},{replacements},{miss_rate}\n"

                with open('../../Experiment-2.csv', 'a') as output_file:
                    output_file.write(line)


def third_experiment(assoc, bsizes):
    nsets = int(256 / assoc)

    for benchmark, benchmark_file in BENCHMARKS.items():
        for cache_experiment, cache in CACHE:
            for bsize in bsizes:
                command = f"./sim-cache -cache:{cache_experiment} {cache_experiment}:{nsets}:{bsize}:{assoc}:l "\
                    + f"-cache:il2 none -cache:{cache} {cache}:256:32:1:l -cache:dl2 none -tlb:itlb none "\
                    + f"-tlb:dtlb none {benchmark_file}"

                output = subprocess.run(
                    command.split(), capture_output=True, text=True).stderr

                instructions, loads_stores, misses, miss_rate, *_ = parse_output(
                    output, cache_experiment)
                line = f"{benchmark},{cache_experiment},{instructions},{loads_stores},{assoc},{bsize},{misses},{miss_rate}\n"

                with open('../../Experiment-3.csv', 'a') as output_file:
                    output_file.write(line)


def fourth_experiment(nsets):
    split_nsets = int(nsets / 2)

    for benchmark, benchmark_file in BENCHMARKS.items():
        # Split cache
        command = f"./sim-cache -cache:il1 il1:{split_nsets}:64:1:l "\
            + f"-cache:il2 none -cache:dl1 dl1:{split_nsets}:64:1:l -cache:dl2 none -tlb:itlb none "\
            + f"-tlb:dtlb none {benchmark_file}"

        output = subprocess.run(
            command.split(), capture_output=True, text=True).stderr

        # Get il1 results
        instructions, loads_stores, misses, miss_rate, *_ = parse_output(
            output, "il1")

        line = f"{benchmark},il1,{instructions},{loads_stores},{split_nsets},{misses},{miss_rate}\n"

        with open('../../Experiment-4.csv', 'a') as output_file:
            output_file.write(line)

        # Get dl1 results
        _, _, misses, miss_rate, *_ = parse_output(
            output, "dl1")

        line = f"{benchmark},dl1,{instructions},{loads_stores},{split_nsets},{misses},{miss_rate}\n"

        with open('../../Experiment-4.csv', 'a') as output_file:
            output_file.write(line)

        # Unified cache
        command = f"./sim-cache -cache:il1 dl1 -cache:dl1 ul1:{nsets}:64:1:l -cache:il2 none "\
            + f"-cache:dl2 none -tlb:itlb none -tlb:dtlb none {benchmark_file}"

        output = subprocess.run(
            command.split(), capture_output=True, text=True).stderr

        instructions, loads_stores, misses, miss_rate, *_ = parse_output(
            output, "ul1")

        line = f"{benchmark},ul1,{instructions},{loads_stores},{nsets},{misses},{miss_rate}\n"

        with open('../../Experiment-4.csv', 'a') as output_file:
            output_file.write(line)


if __name__ == "__main__":
    os.chdir(SIMPLESIM)

    # Experiment-1
    print(
        f"Experiment-1: {len(ASSOC_1) * len(CACHE) * len(BENCHMARKS) * 2} executions...")

    with open('../../Experiment-1.csv', 'w') as output_file:
        output_file.write(
            "Benchmark,Cache,instructions,Loads/Stores,nsets,assoc,misses,miss_rate\n")

    first_experiment(128, ASSOC_1)
    first_experiment(256, ASSOC_2)

    # Experiment-2
    print(
        f"Experiment-2: {len(REPL) * len(CACHE) * len(BENCHMARKS)} executions...")

    with open('../../Experiment-2.csv', 'w') as output_file:
        output_file.write(
            "Benchmark,Cache,instructions,Loads/Stores,repl,misses,replacements,miss_rate\n")

    second_experiment(REPL)

    # Experiment-3
    print(
        f"Experiment-3: {len(BSIZE) * len(CACHE) * len(BENCHMARKS) * 2} executions...")

    with open('../../Experiment-3.csv', 'w') as output_file:
        output_file.write(
            "Benchmark,Cache,instructions,Loads/Stores,assoc,bsize,misses,miss_rate\n")

    third_experiment(1, BSIZE)
    third_experiment(4, BSIZE)

    # Experiment-4
    print("Experiment 4: 4 executions...")

    with open('../../Experiment-4.csv', 'w') as output_file:
        output_file.write(
            "Benchmark,Cache,instructions,Loads/Stores,nsets,misses,miss_rate\n")

    fourth_experiment(256)
