from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect

from .models import Employee, Payslip

# Create your views here.

# -------------------MAIN PROCESS CODE------------------


def hello_world(request):
    return render(request, "payroll_app/hello_world.html")


@csrf_protect
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, "payroll_app/employee_list.html", {"employees": employees})


@csrf_protect
def calculate_overtime_pay(request, pk):
    employee = Employee.objects.get(pk=pk)
    OT_hour_str = request.POST.get("overtime_hour")

    if OT_hour_str == "":
        messages.error(request, "No Overtime Hours added!")
        return redirect("employee_list")
    else:
        try:
            Overtime_Hour = float(OT_hour_str)
        except TypeError:
            messages.error(request, "Invalid Hour!")
            return redirect("employee_list")

    Rate = float(employee.rate)
    ot_pay = (Rate / 160) * Overtime_Hour * 1.5
    final_ot_pay = employee.overtime_pay + ot_pay
    Employee.objects.filter(pk=pk).update(overtime_pay=final_ot_pay)
    # Insert calculate here
    # message.error("FUCK")
    return redirect("employee_list")


@csrf_protect
def employee_detail(request, pk):
    employee = Employee.objects.get(pk=pk)
    return render(request, "employee_detail.html", {"employee": employee})


@csrf_protect
def create_employee(request):
    if request.method == "POST":
        name = request.POST.get("name")
        id_number = request.POST.get("id_number")
        rate = request.POST.get("rate")
        overtime_pay = 0.0
        allowance = request.POST.get("allowance")
        Employee.objects.create(
            name=name,
            id_number=id_number,
            rate=rate,
            overtime_pay=overtime_pay,
            allowance=allowance,
        )
        return redirect("employee_list")
    else:
        return render(request, "payroll_app/create_employee.html")


@csrf_protect
def delete_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.delete()
    return redirect("employee_list")


@csrf_protect
def update_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        employee.name = request.POST.get("name")
        employee.id_number = request.POST.get("id_number")
        employee.rate = request.POST.get("rate")
        # employee.overtime_pay = request.POST.get('overtime_pay')
        employee.allowance = request.POST.get("allowance")
        employee.save()
        return redirect("employee_list")
    else:
        return render(
            request, "payroll_app/update_employee.html", {"employee": employee}
        )


@csrf_protect
def payslips_page(request):
    employees = Employee.objects.all()
    payslips = Payslip.objects.all()
    return render(
        request,
        "payroll_app/payslips_page.html",
        {"employees": employees, "payslips": payslips},
    )


@csrf_protect
def create_payslip(request):
    created_payslips = Payslip.objects.all()
    employee_objects = Employee.objects.all()
    if request.method == "POST":
        employee_pay = request.POST.get("employee_pay")
        month = request.POST.get("month")
        year = request.POST.get("year")
        pay_cycle = request.POST.get("pay_cycle")

        try:
            int(year)
        except ValueError:
            messages.error(request, "Year is not number!")
            return redirect("payslips_page")

        if employee_pay == "all":
            for employee in employee_objects:
                existing_payslips = Payslip.objects.filter(
                    id_number=employee, month=month, year=year, pay_cycle=pay_cycle
                )
                if existing_payslips.exists():
                    messages.error(
                        request,
                        "Payslips already exist for the selected month and year.",
                    )
                    return redirect("payslips_page")
                else:
                    cycle_Xor(pay_cycle, employee, month, year)
            return redirect("payslips_page")
        else:
            employee = Employee.objects.get(pk=employee_pay)
            if employee:
                existing_payslips = Payslip.objects.filter(
                    id_number=employee, month=month, year=year, pay_cycle=pay_cycle
                )
                if existing_payslips.exists():
                    messages.error(
                        request,
                        "Payslips already exist for the selected month and year.",
                    )
                    return redirect("payslips_page")
                else:
                    cycle_Xor(pay_cycle, employee, month, year)
                    return redirect("payslips_page")
            else:
                messages.error(request, "Employee does not exist.")
                return redirect("payslips_page")

    else:
        return render(
            request,
            "payroll_app/create_payslip.html",
            {"payslips": created_payslips, "employees": employee_objects},
        )


@csrf_protect
def payslip_details(
    request, pk
):  # edit this for specific html template for the correct cycle
    payslips = get_object_or_404(Payslip, pk=pk)
    if payslips.pay_cycle == 1:
        return render(request, "payroll_app/view_payslips.html", {"payslips": payslips})
    elif payslips.pay_cycle == 2:
        return render(request, "payroll_app/view_payslips.html", {"payslips": payslips})


# -------------------------- SUPPORT PROCESS CODE--------------------------
def cycle_Xor(pay_cycle, employee, month, year):
    if pay_cycle == "1":
        rate = employee.rate
        allowances = employee.allowance
        overtime = employee.overtime_pay
        pag_ibig = 100

        total_pay, tax = calculate_cycle_1_total_pay(
            rate, allowances, overtime, pag_ibig
        )
        date_range = " 1 - 15"
        Payslip.objects.create(
            id_number=employee,
            month=month,
            date_range=date_range,
            year=year,
            pay_cycle=pay_cycle,
            rate=rate,
            earnings_allowance=allowances,
            pag_ibig=pag_ibig,
            deductions_tax=tax,
            overtime=overtime,
            total_pay=total_pay,
        )
        Employee.objects.filter(pk=employee.pk).update(overtime_pay=0.0)

    elif pay_cycle == "2":
        rate = employee.rate
        allowances = employee.allowance
        overtime = employee.overtime_pay
        philhealth = rate * 0.04
        sss = rate * 0.045

        total_pay, tax = calculate_cycle_2_total_pay(
            rate, allowances, overtime, philhealth, sss
        )
        date_range = " 16 - 30"
        Payslip.objects.create(
            id_number=employee,
            month=month,
            date_range=date_range,
            year=year,
            pay_cycle=pay_cycle,
            rate=rate,
            deductions_health=philhealth,
            deductions_tax=tax,
            sss=sss,
            overtime=overtime,
            total_pay=total_pay,
        )
        Employee.objects.filter(pk=employee.pk).update(overtime_pay=0.0)


def calculate_cycle_1_total_pay(rate, allowances, overtime, pag_ibig):
    tax = ((rate / 2) + allowances + overtime - pag_ibig) * 0.2
    initial_pay = (rate / 2) + allowances + overtime - pag_ibig
    total_pay = initial_pay - tax
    return total_pay, tax


def calculate_cycle_2_total_pay(rate, allowances, overtime, philhealth, sss):
    tax = ((rate / 2) + allowances + overtime - philhealth - sss) * 0.2
    initial_pay = (rate / 2) + allowances + overtime - philhealth - sss
    total_pay = initial_pay - tax
    return total_pay, tax
