import bin_analysis
import filesystem
import scan

if __name__ == "__main__":
    bin_analysis.json_fix()
    bin_analysis.json_fix2()
    scan.scan2json()

    filesystem.extract_filesystem()
    #  check the content of files extracted by binwalk.

    bin_analysis.prepare_analysis()

    bin_analysis.analysis()

