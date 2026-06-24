from config import SAP_SCHEMA


GET_INVOICES = f'SELECT TOP 100 * FROM "{SAP_SCHEMA}"."OINV"'

GET_PAGO_EFECTUADO = """
                    SELECT 
                        T2."CardCode"
                        ,T2."LicTradNum"
                        ,T2."CardName"
                        ,T3."BankName"
                        ,T2."DflAccount"
                        ,T1."Debit"
                        ,T1."LineMemo"
                        ,T1."Ref1"
                    FROM {schema}.JDT1  T1
                    LEFT JOIN {schema}.OCRD T2
                        ON T1."ShortName"=T2."CardCode"
                    LEFT JOIN {schema}.ODSC T3
                        ON T2."BankCode"=T3."BankCode"
                    where "TransId"=? and T1."Debit">0

                """.format(schema=SAP_SCHEMA)

# GET_PAGO_EFECTUADO2 = """
#                     SELECT 
#                         T2."CardCode"
#                         ,T2."LicTradNum"
#                         ,T2."CardName"
#                         ,T3."BankName"
#                         ,T2."DflAccount"
#                         ,T1."Debit"
#                         ,T1."LineMemo"
#                         ,T1."Ref1"
#                         ,T1."Ref2"
#                     FROM SBO_RASH_PRODUCCION.JDT1  T1  
#                     LEFT JOIN SBO_RASH_PRODUCCION.OCRD T2
#                         ON T1."ShortName"=T2."CardCode"
#                     LEFT JOIN SBO_RASH_PRODUCCION.ODSC T3 
#                         ON T2."BankCode"=T3."BankCode"
#                     where "TransId"=? and T1."Debit">0

#                 """
