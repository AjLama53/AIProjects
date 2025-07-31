import pandas as pd
import sys


def find_dropped(sem1, sem2):
    dropped_students = []
    for name1 in sem1["Name"]:
        f1, m2, l1 = name1.split()
        found = False
        for name2 in sem2["Name"]:
            f2, m2, l2 = name2.split()
            if f1 == f2 and l1 == l2:
                found = True
                break
        if not found:
            dropped_students.append(name1)

    return dropped_students


def summary_statistics(semesterID, sem1, sem2):

    if semesterID == "1":
        print(f"Mean of test 1 scores: {sem1['Test1'].mean()}")
        print(f"Standard Deviation of test 1 scores: {sem1['Test1'].std()}")
        print(f"Number of test 1 takers: {sem1['Test1'].count()}")
        print()

        print(f"Mean of test 2 scores: {sem1['Test2'].mean()}")
        print(f"Standard Deviation of test 2 scores: {sem1['Test2'].std()}")
        print(f"Number of test 2 takers: {sem1['Test2'].count()}")

    elif semesterID == "2":
        print(f"Mean of test 1 scores: {sem2['Test1'].mean()}")
        print(f"Standard Deviation of test 1 scores: {sem2['Test1'].std()}")
        print(f"Number of test 1 takers: {sem2['Test1'].count()}")
        print()

        print(f"Mean of test 2 scores: {sem2['Test2'].mean()}")
        print(f"Standard Deviation of test 2 scores: {sem2['Test2'].std()}")
        print(f"Number of test 2 takers: {sem2['Test2'].count()}")

    else:
        print("Enter a valid semester")
        print()

    return None

def student_performance(studentName, sem1, sem2):
    test_scores = []
    firstName, lastName = studentName.split()

    for i in range(len(sem1)):
        if sem1["Name"][i].startswith(firstName) and sem1["Name"][i].endswith(lastName):
            test_scores.append(str(sem1["Test1"][i]))
            test_scores.append(str(sem1["Test2"][i]))

    if not test_scores:
        return "No student with that name"
    
    for i in range(len(sem2)):
        if sem2["Name"][i].startswith(firstName) and sem2["Name"][i].endswith(lastName):
            test_scores.append(str(sem2["Test1"][i]))
            test_scores.append(str(sem2["Test2"][i]))

    return test_scores


def cutoff_report(cutoffScore, semesterID, examID, sem1, sem2):
    students = []

    if semesterID == "1":
        for i in range(len(sem1)):
            if examID == "1":
                if sem1["Test1"][i] < cutoffScore:
                    students.append(sem1["Name"][i])
            elif examID == "2":
                if sem1["Test2"][i] < cutoffScore:
                    students.append(sem1["Name"][i])

    elif semesterID == "2":
        for i in range(len(sem2)):
            if examID == "1":
                if sem2["Test1"][i] < cutoffScore:
                    students.append(sem1["Name"][i])
            elif examID == "2":
                if sem2["Test2"][i] < cutoffScore:
                    students.append(sem1["Name"][i])

    return students

    

        










def main():
    print()
    print("Welcome to RMS: Roster Management Portal")
    print()


    print("Command List:")
    print("Find Dropped- finds students who dropped the course over the break")
    print("Summary Statistics- provides basic statistics for specfic semesters")
    print("Student Performance- provides exam scores for a given student")
    print("Cutoff Report- provides a list of students who have scored less than a given cutoff score", end="\n\n")

    sem1 = pd.read_csv("semester1.txt", sep=';', header=None)
    sem1.columns = ["Name", "Test1", "Test2"]
    sem2 = pd.read_csv("semester2.txt", sep=';', header=None)
    sem2.columns = ["Name", "Test1", "Test2"]

    while True:
        command = input("Enter a command: ").lower()

        if command == "find dropped":
            print(", ".join(find_dropped(sem1, sem2)))
            print()
        
        elif command == "summary statistics":
            sem = input("Please enter a semester: ")
            print()
            summary_statistics(sem, sem1, sem2)
            print()


        elif command == "student performance":
            name = input("Please enter a student name: ").title()
            print()
            print(", ".join(student_performance(name, sem1, sem2)))
            print()

        elif command == "cutoff report":
            cutoffScore = int(input("Please enter a cutoff score: "))
            semesterID = input("Please enter a semester: ")
            examID = input("Please enter a test: ")
            print(", ".join(cutoff_report(cutoffScore, semesterID, examID, sem1, sem2)))
            print()

        else:
            print("Please enter a valid command")
            print()


        while True:
            print("Continue in Portal: Yes or No")
            cont = input().lower()

            if cont == "no":
                sys.exit()

            elif cont != "yes":
                print("Enter a valid command")
                print()

            else:
                break



        

if __name__ == "__main__":
    main()