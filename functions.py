from fpdf import FPDF
import pandas as pd
import datetime

#def generate_PDF(saved_graph):
 #   pdf = FPDF()
  #  pdf.add_page()
   # pdf.image(saved_graph, x = None, y = None, w = 0, h = 0, type = '', link = '')
    #pdf.output('bostadsplan.pdf', 'F')
def dataframe_creation(bank_loan = 0, down_payment = 0, other_loan = 0, 
                       amortization_rate = 0, interest_rate = 0, payback_other = 0, 
                       salary = 0, tax = 0, months_overview = 1, start_date = pd.to_datetime(datetime.datetime.today())):

    original_bank_loan = bank_loan
    df = pd.DataFrame(columns = ['bank_loan', 'other_loan', 'amortization','interest', 'salary_left', 'total_payed', 'date'])
    interest = (interest_rate/100)/12 * bank_loan
    amortization = (amortization_rate/100)/12 * original_bank_loan
    net_salary = salary * (100-tax)/100
    salary_left = net_salary - (amortization + interest + payback_other)
    total_payed = down_payment
    current_date = start_date

    
    df.loc[0, 'bank_loan'] = bank_loan
    df.loc[0, 'other_loan'] = other_loan
    df.loc[0, 'amortization'] = amortization
    df.loc[0, 'interest'] = interest
    df.loc[0, 'salary_left'] = salary_left
    df.loc[0, 'total_payed'] = total_payed
    df.loc[0, 'date'] = start_date
    
    for i in range(months_overview):
        bank_loan = bank_loan - df.loc[i, 'amortization']
        
        
        if((other_loan - payback_other) < 0):
            payback_other = other_loan
            total_payed = total_payed + payback_other
            other_loan = other_loan - payback_other
            df.loc[i+1, 'other_loan'] = other_loan
            payback_other = 0
        elif((other_loan - payback_other) == 0):
            total_payed = total_payed + payback_other
            df.loc[i+1, 'other_loan'] = other_loan - payback_other
            other_loan = 0
            payback_other = 0
        else:
            other_loan = other_loan - payback_other
            total_payed = total_payed + payback_other
            df.loc[i+1, 'other_loan'] = other_loan
        
        
        amortization = (amortization_rate/100)/12 * original_bank_loan
        interest = (interest_rate/100)/12 * bank_loan
        salary_left = net_salary - (amortization + interest + payback_other)
        total_payed = total_payed + amortization
        current_date = current_date + pd.DateOffset(months = 1)
        
        df.loc[i+1, 'bank_loan'] = bank_loan
        df.loc[i+1, 'amortization'] = amortization
        df.loc[i+1, 'interest'] = interest
        df.loc[i+1, 'salary_left'] = salary_left
        df.loc[i+1, 'total_payed'] = total_payed
        df.loc[i+1, 'date'] = current_date

    return df
