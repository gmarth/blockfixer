import subprocess
import time
import sys

class hdd_repair:
    device = None
    test = None
    state = None
    lba = None
    process = 0
    interval = None
    def __init__(self, device):
        self.device = device

        print(f"Starting short test.")
        self.test_drive("short", 10)
        print(f"Starting long test.")
        self.test_drive("long", 60)


    def test_drive(self, test, interval):
        # start test
        self.read_status()
        if self.state == "Passed":
            self.start_test(test)

        while True:
            self.read_status()
            if self.state == "Running":
                pass
            if self.state == "Passed":
                print(f"{test} test Passed without errors.")
                break
            if self.state == "Failed":
                self.write_block(self.lba // 8)
                self.start_test(test)
            time.sleep(interval)

    def start_test(self, test_type):
        completed_process = subprocess.run(["smartctl", "-t", test_type, self.device], capture_output=True, text=True)
        self.process = None
        self.lba = None

    def read_status(self):
        completed_process = subprocess.run(["/usr/sbin/smartctl", "-l", "selftest", device], capture_output=True, text=True)

        output = completed_process.stdout
        lines = output.strip().split("\n")

        for line in lines:
            if "# 1" in line:
                if "Completed: read failure" in line:
                    sector = line.split()[-1]
                    self.process = line.split()[-3]
                    print(f"Test failed. LBA of first error at: {sector}")
                    self.state = "Failed"
                    self.lba = int(sector)
                    break
                if "Self-test routine in progress" in line:
                    if self.process != line.split()[-3]:
                        self.process = line.split()[-3]
                        print(self.process)
                    self.state = "Running"
                    break
                if "Completed without error" in line:
                    self.state = "Passed"
                    break

        return None

    def write_block(block):
        # dd if=/dev/zero of=/dev/sda conv=sync bs=4096 count=1 seek=5590620
        print(f"Writing Block {str(block)}...")
        completed_process = subprocess.run(["dd", "if=/dev/zero", f"of={self.device}", "conv=sync", "bs=4096", "count=1", f"seek={str(block)}"], capture_output=True, text=True)
        completed_process = subprocess.run(["sync"], capture_output=True, text=True)

def get_corrupted_sector(device):
    completed_process = subprocess.run(["/usr/sbin/smartctl", "-l", "selftest", device], capture_output=True, text=True)

    output = completed_process.stdout
    lines = output.strip().split("\n")

    for line in lines:
        if "# 1" in line:
            print(line)
            if "Completed: read failure" in line:
                sector = line.split()[-1]
                print(f"Test failed. LBA of first error at: {sector}")
                return int(sector)

    return None

def still_running(device):
    completed_process = subprocess.run(["/usr/sbin/smartctl", "-l", "selftest", device], capture_output=True, text=True)

    output = completed_process.stdout
    lines = output.strip().split("\n")

    for line in lines:
        if "# 1" in line:
            if "Self-test routine in progress" in line:
                return True

    return False





def self_test(device, type):
    completed_process = subprocess.run(["smartctl", "-t", type, device], capture_output=True, text=True)

def main():
    device = sys.argv[1]
    test_type = sys.argv[2]
    interval = int(sys.argv[3])

    while True:
        print(f"Starte den SMART-Test ({test_type}) für das Gerät {device}...")
        self_test(device, test_type)

        while still_running(device):
            time.sleep(interval)

        corrupted_sector = get_corrupted_sector(device)

        if(corrupted_sector is None):
            break;

        write_sector(device, corrupted_sector)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("example: python script.py /dev/sda")
        sys.exit(1)

        # main()
    device = sys.argv[1]
    test = hdd_repair(device)
