from django.db import models
from django.utils import timezone


class Employee(models.Model):
    name = models.CharField(max_length=255)
    id_number = models.CharField(max_length=20)
    rate = models.FloatField()
    overtime_pay = models.FloatField(blank=True, null=True)
    allowance = models.FloatField(blank=True, null=True)

    def getName(self):
        return self.name

    def getID(self):
        return self.id_number

    def getRate(self):
        return self.rate

    def getOvertime(self):
        return self.overtime_pay

    def resetOvertime(self):
        self.overtime_pay = 0
        self.save()

    def getAllowance(self):
        return self.allowance

    def __str__(self):
        return f"pk: {self.id_number}, rate: {self.rate}"


class Payslip(models.Model):
    id_number = models.ForeignKey(Employee, on_delete=models.CASCADE)

    month = models.CharField(max_length=255)
    date_range = models.CharField(max_length=255)
    year = models.CharField(max_length=255)

    pay_cycle = models.IntegerField()
    rate = models.FloatField(blank=True, null=True)
    earnings_allowance = models.FloatField(blank=True, null=True)

    deductions_tax = models.FloatField(blank=True, null=True)
    deductions_health = models.FloatField(blank=True, null=True)
    pag_ibig = models.FloatField(blank=True, null=True)

    sss = models.FloatField(blank=True, null=True)
    overtime = models.FloatField(blank=True, null=True)
    total_pay = models.FloatField(blank=True, null=True)

    def getIDNumber(self):
        return self.id_number

    def getMonth(self):
        return self.month

    def getYear(self):
        return self.year

    def getPay_cycle(self):
        return self.pay_cycle

    def getRate(self):
        return self.rate

    def getCycleRate(self):
        return self.rate / 2

    def getEarnings_allownce(self):
        return self.earnings_allowance

    def getDeductions_tax(self):
        return self.deductions_tax

    def getDeductions_health(self):
        return self.deductions_health

    def getPag_ibig(self):
        return self.pag_ibig

    def getSSS(self):
        return self.sss

    def getOvertime(self):
        return self.overtime

    def getTotal_pay(self):
        return self.total_pay

    def __str__(self):
        return f"pk: {self.pk}, Employee: {Employee.id_number}, Period: {self.month} {self.date_range} {self.year}, Cycle:{self.pay_cycle}, Total Pay:{self.total_pay}"
