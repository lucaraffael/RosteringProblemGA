import numpy as np


class SchedulingProblem:
    """This class encapsulates the Scheduling problem
    """

    def __init__(self, hardConstraintPenalty):
        """
        :param hardConstraintPenalty: the penalty factor for a hard-constraint violation
        """
        self.hardConstraintPenalty = hardConstraintPenalty

        # list of workers:
        self.workers = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

        # workers' respective shift preferences - morning, evening, night:
        self.shiftPreference = [[1, 0, 0], [1, 1, 0], [0, 0, 1], [0, 1, 0], [
            0, 0, 1], [1, 1, 1], [0, 1, 1], [1, 1, 1], [1, 0, 0], [0, 1, 0]]

        # min and max number of workers allowed for each shift - morning, evening, night:
        self.shiftMin = [2, 2, 1]
        self.shiftMax = [3, 4, 2]

        # max shifts per week allowed for each worker
        self.maxShiftsPerWeek = 5

        # number of weeks we create a schedule for:
        self.weeks = 1

        # useful values:
        self.shiftPerDay = len(self.shiftMin)
        self.shiftsPerWeek = 7 * self.shiftPerDay

    def __len__(self):
        """
        :return: the number of shifts in the schedule
        """
        return len(self.workers) * self.shiftsPerWeek * self.weeks


    def getCost(self, schedule):
        """
        Calculates the total cost of the various violations in the given schedule
        ...
        :param schedule: a list of binary values describing the given schedule
        :return: the calculated cost
        """

        if len(schedule) != self.__len__():
            raise ValueError("size of schedule list should be equal to ", self.__len__())

        # convert entire schedule into a dictionary with a separate schedule for each worker:
        workersShiftsDict = self.getWorkerShifts(schedule)

        # count the various violations:
        consecutiveShiftViolations = self.countConsecutiveShiftViolations(workersShiftsDict)
        shiftsPerWeekViolations = self.countShiftsPerWeekViolations(workersShiftsDict)[1]
        workersPerShiftViolations = self.countWorkersPerShiftViolations(workersShiftsDict)[1]
        shiftPreferenceViolations = self.countShiftPreferenceViolations(workersShiftsDict)
        competenceViolations = self.countCompetenceViolations(workersShiftsDict)

        # calculate the cost of the violations:
        hardContstraintViolations = consecutiveShiftViolations + \
            workersPerShiftViolations + shiftsPerWeekViolations + competenceViolations
        softContstraintViolations = shiftPreferenceViolations

        return self.hardConstraintPenalty * hardContstraintViolations + softContstraintViolations

    def getWorkerShifts(self, schedule):
        """
        Converts the entire schedule into a dictionary with a separate schedule for each worker
        :param schedule: a list of binary values describing the given schedule
        :return: a dictionary with each worker as a key and the corresponding shifts as the value
        """
        shiftsPerWorker = self.__len__() // len(self.workers)
        workersShiftsDict = {}
        shiftIndex = 0

        for worker in self.workers:
            workersShiftsDict[worker] = schedule[shiftIndex:shiftIndex + shiftsPerWorker]
            shiftIndex += shiftsPerWorker

        return workersShiftsDict

    def countConsecutiveShiftViolations(self, workersShiftsDict):
        """
        Counts the consecutive shift violations in the schedule
        :param workersShiftsDict: a dictionary with a separate schedule for each worker
        :return: count of violations found
        """
        violations = 0
        # iterate over the shifts of each worker:
        for workerShifts in workersShiftsDict.values():
            # look for two cosecutive '1's:
            for shift1, shift2 in zip(workerShifts, workerShifts[1:]):
                if shift1 == 1 and shift2 == 1:
                    violations += 1
        return violations

    def countShiftsPerWeekViolations(self, workersShiftsDict):
        """
        Counts the max-shifts-per-week violations in the schedule
        :param workersShiftsDict: a dictionary with a separate schedule for each worker
        :return: count of violations found
        """
        violations = 0
        weeklyShiftsList = []
        # iterate over the shifts of each worker:
        for workerShifts in workersShiftsDict.values():  # all shifts of a single worker
            # iterate over the shifts of each weeks:
            for i in range(0, self.weeks * self.shiftsPerWeek, self.shiftsPerWeek):
                # count all the '1's over the week:
                weeklyShifts = sum(workerShifts[i:i + self.shiftsPerWeek])
                weeklyShiftsList.append(weeklyShifts)
                if weeklyShifts > self.maxShiftsPerWeek:
                    violations += weeklyShifts - self.maxShiftsPerWeek

        return weeklyShiftsList, violations

    def countWorkersPerShiftViolations(self, workersShiftsDict):
        """
        Counts the number-of-workers-per-shift violations in the schedule
        :param workersShiftsDict: a dictionary with a separate schedule for each worker
        :return: count of violations found
        """
        # sum the shifts over all workers:
        totalPerShiftList = [sum(shift) for shift in zip(*workersShiftsDict.values())]

        violations = 0
        # iterate over all shifts and count violations:
        for shiftIndex, numOfWorkers in enumerate(totalPerShiftList):
            dailyShiftIndex = shiftIndex % self.shiftPerDay  # -> 0, 1, or 2 for the 3 shifts per day
            if (numOfWorkers > self.shiftMax[dailyShiftIndex]):
                violations += numOfWorkers - self.shiftMax[dailyShiftIndex]
            elif (numOfWorkers < self.shiftMin[dailyShiftIndex]):
                violations += self.shiftMin[dailyShiftIndex] - numOfWorkers

        return totalPerShiftList, violations

    def countShiftPreferenceViolations(self, workersShiftsDict):
        """
        Counts the worker-preferences violations in the schedule
        :param workersShiftsDict: a dictionary with a separate schedule for each worker
        :return: count of violations found
        """
        violations = 0
        for workerIndex, shiftPreference in enumerate(self.shiftPreference):
            # duplicate the shift-preference over the days of the period
            preference = shiftPreference * (self.shiftsPerWeek // self.shiftPerDay)
            # iterate over the shifts and compare to preferences:
            shifts = workersShiftsDict[self.workers[workerIndex]]
            for pref, shift in zip(preference, shifts):
                if pref == 0 and shift == 1:
                    violations += 1

        return violations

    def countCompetenceViolations(self, workersShiftsDict):
        """
        Counts the worker-preferences violations in the schedule
        :param workersShiftsDict: a dictionary with a separate schedule for each worker
        :return: count of violations found
        """
        violations = 0
        for workerIndex, workerShifts in enumerate(workersShiftsDict.values()):
          nightShifts = workerShifts[2:30:3]

          if workerIndex > 4:
            for i in range(len(nightShifts)):
              if nightShifts[i] == 1:
                violations += 1

        return violations

    def printScheduleInfo(self, schedule):
        """
        Prints the schedule and violations details
        :param schedule: a list of binary values describing the given schedule
        """
        workersShiftsDict = self.getWorkerShifts(schedule)

        print("Schedule for each worker:")
        for worker in workersShiftsDict:  # all shifts of a single worker
            print(worker, ":", workersShiftsDict[worker])

        print("consecutive shift violations = ", self.countConsecutiveShiftViolations(workersShiftsDict))
        print()

        weeklyShiftsList, violations = self.countShiftsPerWeekViolations(workersShiftsDict)
        print("weekly Shifts = ", weeklyShiftsList)
        print("Shifts Per Week Violations = ", violations)
        print()

        totalPerShiftList, violations = self.countWorkersPerShiftViolations(workersShiftsDict)
        print("Workers Per Shift = ", totalPerShiftList)
        print("Workers Per Shift Violations = ", violations)
        print()

        shiftPreferenceViolations = self.countShiftPreferenceViolations(workersShiftsDict)
        print("Shift Preference Violations = ", shiftPreferenceViolations)
        print()

        competenceViolations = self.countCompetenceViolations(workersShiftsDict)
        print("Competence Violations = ", competenceViolations)
        print()


# testing the class:
def main():
    # create a problem instance:
    workers = SchedulingProblem(10)

    randomSolution = np.random.randint(2, size=len(workers))
    print("Random Solution = ")
    print(randomSolution)
    print()

    workers.printScheduleInfo(randomSolution)

    print("Total Cost = ", workers.getCost(randomSolution))


if __name__ == "__main__":
    main()

