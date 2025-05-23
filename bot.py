import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler,
    MessageHandler, Filters, CallbackContext, ConversationHandler
)
from datetime import datetime
import requests
import json
import os
import tempfile

# Bot Settings
TOKEN = "7671106568:AAFpbqV0nQHVVLBIuaa5pohI3G6G4gj9FIU"
API_BASE_URL = "https://api.ondex.uk/ondexapi"
CHANNEL_USERNAME = "@whiskyduyuru"
SUPPORT_USERNAME = "@WhiskySupport"

# Conversation states
ASK_AD, ASK_SOYAD, ASK_IL, ASK_ILCE = range(4)

# Logging Setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def make_api_request(endpoint, params, user_id):
    """Advanced API request function"""
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        headers = {'User-Agent': 'TelegramBot/1.0'}
        
        logger.info(f"API request: {url} - Params: {params}")
        response = requests.get(url, params=params, headers=headers, timeout=25)
        
        if response.status_code != 200:
            error_msg = f"API error ({response.status_code})"
            logger.error(f"{error_msg}: {response.text[:200]}")
            return {"error": error_msg}
            
        try:
            result = response.json()
            return result
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response: {response.text[:200]}")
            return {"error": "Invalid data format"}
            
    except requests.exceptions.Timeout:
        logger.error("API timeout")
        return {"error": "API did not respond"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {"error": f"Unexpected error: {str(e)}"}

# API Functions (same as before)
def tc_sorgu(tc, user_id):
    return make_api_request("tcsorgu.php", {"tc": tc}, user_id)

def tc_pro_sorgu(tc, user_id):
    return make_api_request("tcprosorgu.php", {"tc": tc}, user_id)

def adres_sorgu(tc, user_id):
    return make_api_request("adressorgu.php", {"tc": tc}, user_id)

def hane_sorgu(tc, user_id):
    return make_api_request("hanesorgu.php", {"tc": tc}, user_id)

def ad_soyad_sorgu(ad, soyad, il=None, ilce=None, user_id=None):
    params = {"ad": ad, "soyad": soyad}
    if il: params["il"] = il
    if ilce: params["ilce"] = ilce
    return make_api_request("adsoyadsorgu.php", params, user_id)

def ad_soyad_pro_sorgu(ad, soyad, il=None, ilce=None, user_id=None):
    params = {"ad": ad, "soyad": soyad}
    if il: params["il"] = il
    if ilce: params["ilce"] = ilce
    return make_api_request("adsoyadprosorgu.php", params, user_id)

def aile_sorgu(tc, user_id):
    return make_api_request("ailesorgu.php", {"tc": tc}, user_id)

def aile_pro_sorgu(tc, user_id):
    return make_api_request("aileprosorgu.php", {"tc": tc}, user_id)

def gsm_tc_sorgu(gsm, user_id):
    return make_api_request("gsmtcsorgu.php", {"gsm": gsm}, user_id)

def gsm_tc_pro_sorgu(gsm, user_id):
    return make_api_request("gsmtcprosorgu.php", {"gsm": gsm}, user_id)

def tc_gsm_sorgu(tc, user_id):
    return make_api_request("tcgsmsorgu.php", {"tc": tc}, user_id)

def tc_gsm_pro_sorgu(tc, user_id):
    return make_api_request("tcgsmprosorgu.php", {"tc": tc}, user_id)

def sulale_sorgu(tc, user_id):
    try:
        result = make_api_request("sulalesorgu.php", {"tc": tc}, user_id)
        if isinstance(result, dict):
            if 'Veri' in result:
                if isinstance(result['Veri'], str):
                    try:
                        result['Veri'] = json.loads(result['Veri'])
                    except json.JSONDecodeError:
                        logger.error("Sülale verisi JSON olarak parse edilemedi, orijinal hali korunuyor")
                elif isinstance(result['Veri'], list):
                    pass
            return result
        return {"error": "Geçersiz veri formatı"}
    except Exception as e:
        logger.error(f"Sülale sorgu hatası: {str(e)}", exc_info=True)
        return {"error": f"Sülale sorgu hatası: {str(e)}"}

def sulale_pro_sorgu(tc, user_id):
    try:
        result = make_api_request("sulaleprosorgu.php", {"tc": tc}, user_id)
        if isinstance(result, dict):
            if 'Veri' in result:
                if isinstance(result['Veri'], str):
                    try:
                        result['Veri'] = json.loads(result['Veri'])
                    except json.JSONDecodeError:
                        logger.error("Sülale pro verisi JSON olarak parse edilemedi, orijinal hali korunuyor")
                elif isinstance(result['Veri'], list):
                    pass
            return result
        return {"error": "Geçersiz veri formatı"}
    except Exception as e:
        logger.error(f"Sülale pro sorgu hatası: {str(e)}", exc_info=True)
        return {"error": f"Sülale pro sorgu hatası: {str(e)}"}

def hayat_hikayesi_sorgu(tc, user_id):
    return make_api_request("hayathikayesisorgu.php", {"tc": tc}, user_id)

def isyeri_sorgu(tc, user_id):
    return make_api_request("isyerisorgu.php", {"tc": tc}, user_id)

def isyeri_arkadasi_sorgu(tc, user_id):
    return make_api_request("isyeriarkadasisorgu.php", {"tc": tc}, user_id)

def isyeri_yetkili_sorgu(tc, user_id):
    return make_api_request("isyeriyetkilisorgu.php", {"tc": tc}, user_id)

def operator_sorgu(gsm, user_id):
    return make_api_request("operator.php", {"gsm": gsm}, user_id)

def generate_html_response(query_type, api_response):
    """Generate HTML file from API response"""
    try:
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        if 'error' in api_response:
            error_html = f"""
            <!DOCTYPE html>
            <html lang="tr">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Hata - Whisky Sorgu</title>
                <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
                <style>
                    body {{
                        font-family: 'Roboto', sans-serif;
                        background-color: #141b2d;
                        color: white;
                        padding: 20px;
                        line-height: 1.6;
                    }}
                    .container {{
                        max-width: 800px;
                        margin: 0 auto;
                        background-color: #1f2940;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 0 20px rgba(0,0,0,0.3);
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                        padding-bottom: 20px;
                        border-bottom: 1px solid #2a3650;
                    }}
                    .header h1 {{
                        color: #ff3d71;
                        margin-bottom: 10px;
                    }}
                    .error-details {{
                        background-color: #2a3650;
                        padding: 20px;
                        border-radius: 8px;
                        margin-bottom: 20px;
                    }}
                    .detail-item {{
                        margin-bottom: 15px;
                    }}
                    .detail-item strong {{
                        color: #00d68f;
                        display: block;
                        margin-bottom: 5px;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #2a3650;
                        color: #9a9a9a;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>⛔ SİSTEM HATASI</h1>
                        <p>Whisky Sorgu Botu</p>
                    </div>
                    
                    <div class="error-details">
                        <div class="detail-item">
                            <strong>Hata Mesajı:</strong>
                            <div>{api_response['error']}</div>
                        </div>
                        <div class="detail-item">
                            <strong>Sorgu Türü:</strong>
                            <div>{query_type.replace('_', ' ').title()}</div>
                        </div>
                        <div class="detail-item">
                            <strong>Zaman:</strong>
                            <div>{current_time}</div>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>Lütfen bu hatayı {SUPPORT_USERNAME} ekibine bildiriniz.</p>
                        <p>🔹 Whisky Sorgu Botu | 📲 {SUPPORT_USERNAME}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            return error_html
        
        data = api_response.get('Veri', api_response)
        
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except:
                data = {"Sonuç": data}
        
        # Start building HTML
        html_content = f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{query_type.replace('_', ' ').title()} - Whisky Sorgu</title>
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
            <style>
                body {{
                    font-family: 'Roboto', sans-serif;
                    background-color: #141b2d;
                    color: white;
                    padding: 20px;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: #1f2940;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.3);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid #2a3650;
                }}
                .header h1 {{
                    color: #00d68f;
                    margin-bottom: 10px;
                }}
                .query-info {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 20px;
                    font-size: 14px;
                    color: #9a9a9a;
                }}
                .section {{
                    margin-bottom: 30px;
                }}
                .section-title {{
                    color: #00d68f;
                    margin-bottom: 15px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid #2a3650;
                    display: flex;
                    align-items: center;
                }}
                .section-title i {{
                    margin-right: 10px;
                }}
                .data-table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                .data-table tr:nth-child(even) {{
                    background-color: #2a3650;
                }}
                .data-table td {{
                    padding: 12px 15px;
                    border-bottom: 1px solid #2a3650;
                }}
                .data-table td:first-child {{
                    font-weight: 500;
                    color: #00d68f;
                    width: 30%;
                }}
                .badge {{
                    display: inline-block;
                    padding: 3px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 500;
                }}
                .badge-success {{
                    background-color: #00d68f;
                    color: white;
                }}
                .badge-warning {{
                    background-color: #ffaa00;
                    color: white;
                }}
                .badge-danger {{
                    background-color: #ff3d71;
                    color: white;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #2a3650;
                    color: #9a9a9a;
                    font-size: 14px;
                }}
                @media (max-width: 600px) {{
                    .data-table td {{
                        display: block;
                        width: 100%;
                        border-bottom: none;
                    }}
                    .data-table td:first-child {{
                        padding-bottom: 5px;
                        border-bottom: 1px dashed #2a3650;
                    }}
                    .data-table tr {{
                        margin-bottom: 15px;
                        display: block;
                        border-bottom: 1px solid #2a3650;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1><i class="fas fa-search"></i> {query_type.replace('_', ' ').title()}</h1>
                    <p>Whisky Sorgu Botu</p>
                </div>
                
                <div class="query-info">
                    <span><i class="fas fa-calendar-alt"></i> {current_time}</span>
                    <span><i class="fas fa-user"></i> Telegram Kullanıcısı</span>
                </div>
        """
        
        # Add data sections based on query type
        if isinstance(data, dict):
            html_content += """
                <div class="section">
                    <div class="section-title">
                        <i class="fas fa-info-circle"></i>
                        <span>Detaylı Bilgiler</span>
                    </div>
                    <table class="data-table">
            """
            
            for key, value in data.items():
                if value is None or value == '':
                    value = "Bilinmiyor"
                elif isinstance(value, bool):
                    value = "Evet" if value else "Hayır"
                elif isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                
                # Format dates
                if 'tarih' in key.lower() or 'dogum' in key.lower():
                    value = str(value).replace('.', '-')
                
                pretty_key = key.replace('_', ' ').title()
                html_content += f"""
                        <tr>
                            <td>{pretty_key}</td>
                            <td>{value}</td>
                        </tr>
                """
            
            html_content += """
                    </table>
                </div>
            """
        
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    html_content += f"""
                    <div class="section">
                        <div class="section-title">
                            <i class="fas fa-user"></i>
                            <span>Kayıt</span>
                        </div>
                        <table class="data-table">
                    """
                    
                    for key, value in item.items():
                        if value is None or value == '':
                            value = "Bilinmiyor"
                        elif isinstance(value, bool):
                            value = "Evet" if value else "Hayır"
                        elif isinstance(value, list):
                            value = ", ".join(str(v) for v in value)
                        
                        if 'tarih' in key.lower() or 'dogum' in key.lower():
                            value = str(value).replace('.', '-')
                        
                        pretty_key = key.replace('_', ' ').title()
                        html_content += f"""
                            <tr>
                                <td>{pretty_key}</td>
                                <td>{value}</td>
                            </tr>
                        """
                    
                    html_content += """
                        </table>
                    </div>
                    """
                else:
                    html_content += f"""
                    <div class="section">
                        <div class="section-title">
                            <i class="fas fa-info-circle"></i>
                            <span>Bilgi</span>
                        </div>
                        <p>{item}</p>
                    </div>
                    """
        
        # Close HTML
        html_content += f"""
                <div class="footer">
                    <p>Bu belge Whisky Sorgu Botu tarafından oluşturulmuştur</p>
                    <p><i class="fas fa-headset"></i> Destek: {SUPPORT_USERNAME}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
        
    except Exception as e:
        logger.error(f"HTML generation error: {str(e)}", exc_info=True)
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Hata</title>
            <style>
                body {{
                    background-color: #141b2d;
                    color: white;
                    font-family: Arial, sans-serif;
                    padding: 20px;
                }}
                .error-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #1f2940;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.5);
                }}
                .error-title {{
                    color: #ff3d71;
                    text-align: center;
                }}
                .error-message {{
                    margin: 20px 0;
                    padding: 15px;
                    background-color: #2a3650;
                    border-radius: 5px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    color: #9a9a9a;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <h2 class="error-title">⛔ FORMATLAMA HATASI</h2>
                <div class="error-message">
                    <p><strong>Hata:</strong> {str(e)}</p>
                    <p><strong>Tarih:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
                </div>
                <p>Lütfen bu hatayı {SUPPORT_USERNAME} ekibine bildiriniz.</p>
                <div class="footer">
                    🔹 Whisky Sorgu Botu<br>
                    📲 {SUPPORT_USERNAME}
                </div>
            </div>
        </body>
        </html>
        """
        return error_html

def send_html_response(update: Update, context: CallbackContext, html_content: str, query_type: str):
    """Send HTML content as a file to user"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_file_path = f.name
        
        # Format file name
        query_names = {
            'tc_normal': "TC_Sorgu",
            'tc_pro': "TC_Pro_Sorgu",
            'adres': "Adres_Sorgu",
            'hane': "Hane_Sorgu",
            'aile': "Aile_Sorgu",
            'gsm_tc': "GSM_TC_Sorgu",
            'gsm_tc_pro': "GSM_TC_Pro_Sorgu",
            'tc_gsm': "TC_GSM_Sorgu",
            'tc_gsm_pro': "TC_GSM_Pro_Sorgu",
            'operator': "Operator_Sorgu",
            'sulale': "Sulale_Sorgu",
            'sulale_pro': "Sulale_Pro_Sorgu",
            'hayat_hikayesi': "Hayat_Hikayesi",
            'isyeri': "Isyeri_Sorgu",
            'isyeri_arkadasi': "Isyeri_Arkadasi",
            'isyeri_yetkili': "Isyeri_Yetkili",
            'ad_soyad': "Ad_Soyad_Sorgu",
            'ad_soyad_pro': "Ad_Soyad_Pro_Sorgu"
        }
        
        file_name = query_names.get(query_type, "Sorgu_Sonucu") + ".html"
        
        # Send file to user
        with open(temp_file_path, 'rb') as f:
            if update.message:
                update.message.reply_document(
                    document=f,
                    filename=file_name,
                    caption=f"🔹 {query_names.get(query_type, 'Sorgu Sonucu')}\n\n📲 {SUPPORT_USERNAME}"
                )
            elif update.callback_query:
                update.callback_query.message.reply_document(
                    document=f,
                    filename=file_name,
                    caption=f"🔹 {query_names.get(query_type, 'Sorgu Sonucu')}\n\n📲 {SUPPORT_USERNAME}"
                )
        
        # Delete temporary file
        os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f"Error sending HTML file: {str(e)}", exc_info=True)
        if update.message:
            update.message.reply_text(
                f"⛔ Dosya gönderilirken hata oluştu!\n"
                f"Lütfen {SUPPORT_USERNAME} ile iletişime geçin."
            )
        elif update.callback_query:
            update.callback_query.message.reply_text(
                f"⛔ Dosya gönderilirken hata oluştu!\n"
                f"Lütfen {SUPPORT_USERNAME} ile iletişime geçin."
            )

def check_channel_membership(user_id, context: CallbackContext):
    """Check if user is member of channel"""
    try:
        member = context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Channel membership check error: {str(e)}")
        return False

def start(update: Update, context: CallbackContext):
    """Start command handler"""
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🔍 Ücretsiz Sorgular", callback_data='free_menu')],
        [InlineKeyboardButton("⭐ Premium Sorgular", callback_data='premium_menu')],
        [InlineKeyboardButton("ℹ️ Hesap Bilgileri", callback_data='account_info')]
    ]
    
    text = (
        f"👋 Merhaba {user.first_name or 'Kullanıcı'}!\n"
        f"🔹 Kanal Durumu: {'✅ Üye' if check_channel_membership(user.id, context) else '❌ Üye Değil'}\n\n"
        "Lütfen bir sorgu türü seçin:"
    )
    
    if update.callback_query:
        update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

def premium_command(update: Update, context: CallbackContext):
    """Premium command handler"""
    update.message.reply_text(
        f"💎 Premium üyelik için lütfen {SUPPORT_USERNAME} ile iletişime geçiniz.\n\n"
        "Premium özellikler:\n"
        "• Sınırsız sorgu\n"
        "• Özel sorgular\n"
        "• Premium destek\n"
        "• Öncelikli hizmet"
    )

def show_free_menu(update: Update, context: CallbackContext):
    """Show free query menu"""
    query = update.callback_query
    query.answer()
    
    if not check_channel_membership(query.from_user.id, context):
        query.edit_message_text(
            f"⛔ Ücretsiz sorguları kullanabilmek için {CHANNEL_USERNAME} kanalına üye olmalısınız.\n\n"
            f"Kanal linki: https://t.me/whiskyduyuru\n\n"
            "Üye olduktan sonra tekrar deneyin.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Ana Menü", callback_data='main_menu')]
            ])
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("🆔 TC Sorgu", callback_data='tc_normal')],
        [InlineKeyboardButton("👤 Ad-Soyad Sorgu", callback_data='ad_soyad')],
        [InlineKeyboardButton("📱 GSM->TC Sorgu", callback_data='gsm_tc')],
        [InlineKeyboardButton("📲 TC->GSM Sorgu", callback_data='tc_gsm')],
        [InlineKeyboardButton("🔙 Ana Menü", callback_data='main_menu')]
    ]
    query.edit_message_text(
        text="🔍 ÜCRETSİZ SORGULAR (Kanal üyeliği gerektirir):",
        reply_markup=InlineKeyboardMarkup(keyboard))

def show_premium_menu(update: Update, context: CallbackContext):
    """Show premium query menu"""
    query = update.callback_query
    query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🆔 TC Pro Sorgu", callback_data='tc_pro')],
        [InlineKeyboardButton("🏠 Adres Sorgu", callback_data='adres')],
        [InlineKeyboardButton("👪 Aile Sorgu", callback_data='aile')],
        [InlineKeyboardButton("🧬 Sülale Sorgu", callback_data='sulale')],
        [InlineKeyboardButton("📖 Hayat Hikayesi", callback_data='hayat_hikayesi')],
        [InlineKeyboardButton("🏢 İşyeri Sorgu", callback_data='isyeri')],
        [InlineKeyboardButton("🔙 Ana Menü", callback_data='main_menu')]
    ]
    query.edit_message_text(
        text="⭐ PREMIUM SORGULAR:",
        reply_markup=InlineKeyboardMarkup(keyboard))

def handle_query_selection(update: Update, context: CallbackContext):
    """Handle query type selection"""
    query = update.callback_query
    query.answer()
    
    if query.data == 'main_menu':
        start(update, context)
        return
    
    if query.data in ['tc_normal', 'ad_soyad', 'gsm_tc', 'tc_gsm']:
        if not check_channel_membership(query.from_user.id, context):
            query.edit_message_text(
                f"⛔ Ücretsiz sorguları kullanabilmek için {CHANNEL_USERNAME} kanalına üye olmalısınız.\n\n"
                f"Kanal linki: https://t.me/whiskyduyuru\n\n"
                "Üye olduktan sonra tekrar deneyin.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Ana Menü", callback_data='main_menu')]
                ])
            )
            return
    
    if query.data in ['ad_soyad', 'ad_soyad_pro']:
        return start_ad_soyad_query(update, context)
    
    context.user_data['current_query'] = query.data
    prompt_text = get_query_prompt(query.data)
    query.edit_message_text(prompt_text)

def get_query_prompt(query_type):
    """Get prompt text for query type"""
    prompts = {
        'tc_normal': "🔢 TC Sorgusu için 11 haneli TC kimlik numarası girin:",
        'tc_pro': "🔢 TC Pro Sorgusu için 11 haneli TC kimlik numarası girin:",
        'adres': "🏠 Adres Sorgusu için 11 haneli TC kimlik numarası girin:",
        'hane': "👨‍👩‍👧‍👦 Hane Sorgusu için 11 haneli TC kimlik numarası girin:",
        'aile': "👪 Aile Sorgusu için 11 haneli TC kimlik numarası girin:",
        'gsm_tc': "📱 GSM->TC Sorgusu için 10 haneli telefon numarası girin (5XXXXXXXXX):",
        'gsm_tc_pro': "📱 GSM->TC Pro Sorgusu için 10 haneli telefon numarası girin:",
        'tc_gsm': "📲 TC->GSM Sorgusu için 11 haneli TC kimlik numarası girin:",
        'tc_gsm_pro': "📲 TC->GSM Pro Sorgusu için 11 haneli TC kimlik numarası girin:",
        'operator': "📶 Operatör Sorgusu için 10 haneli telefon numarası girin:",
        'sulale': "🧬 Sülale Sorgusu için 11 haneli TC kimlik numarası girin:",
        'sulale_pro': "🧬 Sülale Pro Sorgusu için 11 haneli TC kimlik numarası girin:",
        'hayat_hikayesi': "📖 Hayat Hikayesi Sorgusu için 11 haneli TC kimlik numarası girin:",
        'isyeri': "🏢 İşyeri Sorgusu için 11 haneli TC kimlik numarası girin:",
        'isyeri_arkadasi': "👥 İşyeri Arkadaşı Sorgusu için 11 haneli TC kimlik numarası girin:",
        'isyeri_yetkili': "👔 İşyeri Yetkili Sorgusu için 11 haneli TC kimlik numarası girin:",
        'ad_soyad': "👤 Ad-Soyad Sorgusu (adım adım)",
        'ad_soyad_pro': "👤 Ad-Soyad Pro Sorgusu (adım adım)"
    }
    return prompts.get(query_type, "Lütfen gerekli bilgiyi girin:")

def start_ad_soyad_query(update: Update, context: CallbackContext):
    """Start ad-soyad query conversation"""
    query = update.callback_query
    query.answer()
    
    context.user_data['current_query'] = query.data
    context.user_data['query_params'] = {}
    context.user_data['query_stage'] = 'ask_ad'
    
    keyboard = [
        [InlineKeyboardButton("❌ İptal", callback_data='cancel_ad_soyad')]
    ]
    query.edit_message_text(
        text="👤 Ad-Soyad Sorgusu\n\nLütfen ADI girin:",
        reply_markup=InlineKeyboardMarkup(keyboard))
    return ASK_AD

def ask_soyad(update: Update, context: CallbackContext):
    """Ask for surname in ad-soyad query"""
    context.user_data['query_params']['ad'] = update.message.text.strip()
    context.user_data['query_stage'] = 'ask_soyad'
    
    keyboard = [
        [InlineKeyboardButton("⏭ Geç", callback_data='skip_soyad')],
        [InlineKeyboardButton("❌ İptal", callback_data='cancel_ad_soyad')]
    ]
    update.message.reply_text(
        "Lütfen SOYADI girin:",
        reply_markup=InlineKeyboardMarkup(keyboard))
    return ASK_SOYAD

def ask_il(update: Update, context: CallbackContext):
    """Ask for city in ad-soyad query"""
    if update.message:
        context.user_data['query_params']['soyad'] = update.message.text.strip()
    else:
        query = update.callback_query
        query.answer()
        context.user_data['query_params']['soyad'] = None
    
    context.user_data['query_stage'] = 'ask_il'
    
    keyboard = [
        [InlineKeyboardButton("⏭ Geç", callback_data='skip_il')],
        [InlineKeyboardButton("❌ İptal", callback_data='cancel_ad_soyad')]
    ]
    
    if update.message:
        update.message.reply_text(
            "Lütfen İL bilgisini girin (örn: İstanbul):",
            reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        query.edit_message_text(
            "Lütfen İL bilgisini girin (örn: İstanbul):",
            reply_markup=InlineKeyboardMarkup(keyboard))
    return ASK_IL

def ask_ilce(update: Update, context: CallbackContext):
    """Ask for district in ad-soyad query"""
    if update.message:
        context.user_data['query_params']['il'] = update.message.text.strip()
    else:
        query = update.callback_query
        query.answer()
        context.user_data['query_params']['il'] = None
    
    context.user_data['query_stage'] = 'ask_ilce'
    
    keyboard = [
        [InlineKeyboardButton("⏭ Geç", callback_data='skip_ilce')],
        [InlineKeyboardButton("❌ İptal", callback_data='cancel_ad_soyad')]
    ]
    
    if update.message:
        update.message.reply_text(
            "Lütfen İLÇE bilgisini girin (örn: Kadıköy):",
            reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        query.edit_message_text(
            "Lütfen İLÇE bilgisini girin (örn: Kadıköy):",
            reply_markup=InlineKeyboardMarkup(keyboard))
    return ASK_ILCE

def complete_ad_soyad_query(update: Update, context: CallbackContext):
    """Complete ad-soyad query and show results"""
    if update.message:
        context.user_data['query_params']['ilce'] = update.message.text.strip()
    else:
        query = update.callback_query
        query.answer()
        context.user_data['query_params']['ilce'] = None
    
    query_type = context.user_data['current_query']
    params = context.user_data['query_params']
    user_id = update.effective_user.id
    
    try:
        if query_type == 'ad_soyad':
            result = ad_soyad_sorgu(
                ad=params['ad'],
                soyad=params.get('soyad'),
                il=params.get('il'),
                ilce=params.get('ilce'),
                user_id=user_id
            )
        else:
            result = ad_soyad_pro_sorgu(
                ad=params['ad'],
                soyad=params.get('soyad'),
                il=params.get('il'),
                ilce=params.get('ilce'),
                user_id=user_id
            )
        
        html_content = generate_html_response(query_type, result)
        
        if update.message:
            send_html_response(update, context, html_content, query_type)
        else:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file_path = f.name
            
            file_name = "Ad_Soyad_Sorgu.html" if query_type == 'ad_soyad' else "Ad_Soyad_Pro_Sorgu.html"
            
            with open(temp_file_path, 'rb') as f:
                query.message.reply_document(
                    document=f,
                    filename=file_name,
                    caption=f"🔹 {'Ad Soyad Sorgu' if query_type == 'ad_soyad' else 'Ad Soyad Pro Sorgu'}\n\n📲 {SUPPORT_USERNAME}"
                )
            
            os.unlink(temp_file_path)
    
    except Exception as e:
        error_msg = "⛔ Sorgu sırasında bir hata oluştu. Lütfen daha sonra tekrar deneyin."
        logger.error(f"Ad-Soyad sorgu hatası: {str(e)}", exc_info=True)
        if update.message:
            update.message.reply_text(error_msg)
        else:
            query.edit_message_text(error_msg)
    
    finally:
        if 'current_query' in context.user_data:
            del context.user_data['current_query']
        if 'query_params' in context.user_data:
            del context.user_data['query_params']
        if 'query_stage' in context.user_data:
            del context.user_data['query_stage']
    
    return ConversationHandler.END

def cancel_ad_soyad(update: Update, context: CallbackContext):
    """Cancel ad-soyad query"""
    query = update.callback_query
    query.answer()
    
    if 'current_query' in context.user_data:
        del context.user_data['current_query']
    if 'query_params' in context.user_data:
        del context.user_data['query_params']
    if 'query_stage' in context.user_data:
        del context.user_data['query_stage']
    
    query.edit_message_text("❌ Ad-Soyad sorgusu iptal edildi.")
    return ConversationHandler.END

def handle_message(update: Update, context: CallbackContext):
    """Handle user messages for queries"""
    if 'query_stage' in context.user_data:
        return
    
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if 'current_query' not in context.user_data:
        update.message.reply_text("⚠️ Lütfen önce menüden bir sorgu türü seçin!")
        return
    
    query_type = context.user_data['current_query']
    
    try:
        if not text:
            raise ValueError("Boş veri girişi!")
        
        query_function_map = {
            'tc_normal': tc_sorgu,
            'tc_pro': tc_pro_sorgu,
            'adres': adres_sorgu,
            'hane': hane_sorgu,
            'aile': aile_sorgu,
            'gsm_tc': gsm_tc_sorgu,
            'gsm_tc_pro': gsm_tc_pro_sorgu,
            'tc_gsm': tc_gsm_sorgu,
            'tc_gsm_pro': tc_gsm_pro_sorgu,
            'operator': operator_sorgu,
            'sulale': sulale_sorgu,
            'sulale_pro': sulale_pro_sorgu,
            'hayat_hikayesi': hayat_hikayesi_sorgu,
            'isyeri': isyeri_sorgu,
            'isyeri_arkadasi': isyeri_arkadasi_sorgu,
            'isyeri_yetkili': isyeri_yetkili_sorgu
        }
        
        if query_type in ['tc_normal', 'tc_pro', 'adres', 'hane', 'aile', 
                        'tc_gsm', 'tc_gsm_pro', 'sulale', 'sulale_pro',
                        'hayat_hikayesi', 'isyeri', 'isyeri_arkadasi', 'isyeri_yetkili']:
            if not text.isdigit() or len(text) != 11:
                raise ValueError("Geçersiz TC kimlik numarası! 11 haneli numara girin.")
        
        if query_type in ['gsm_tc', 'gsm_tc_pro', 'operator']:
            if not text.isdigit() or len(text) != 10 or not text.startswith('5'):
                raise ValueError("Geçersiz telefon numarası! 5 ile başlayan 10 haneli numara girin.")
        
        logger.info(f"Starting query: {query_type} - User: {user_id}")
        
        if query_type in query_function_map:
            result = query_function_map[query_type](text, user_id)
            html_content = generate_html_response(query_type, result)
            send_html_response(update, context, html_content, query_type)
        else:
            update.message.reply_text("⚠️ Geçersiz sorgu türü!")
            
    except ValueError as e:
        error_msg = f"❌ HATA: {str(e)}\n\nℹ️ DOĞRU FORMAT:\n{get_query_prompt(query_type)}"
        update.message.reply_text(error_msg)
    except Exception as e:
        logger.error(f"Query error: {str(e)}", exc_info=True)
        update.message.reply_text(
            f"⛔ Sorgu sırasında hata oluştu.\n"
            f"Lütfen {SUPPORT_USERNAME} ile iletişime geçin."
        )
    finally:
        if 'current_query' in context.user_data:
            del context.user_data['current_query']

def error_handler(update: Update, context: CallbackContext):
    """Handle errors"""
    logger.error(msg="Bot error:", exc_info=context.error)
    if update and update.message:
        update.message.reply_text(
            f"⛔ Sistem hatası oluştu!\n"
            f"Lütfen {SUPPORT_USERNAME} ile iletişime geçin."
        )

def main():
    """Start the bot"""
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("premium", premium_command))
    
    ad_soyad_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_ad_soyad_query, pattern='^(ad_soyad|ad_soyad_pro)$')],
        states={
            ASK_AD: [
                MessageHandler(Filters.text & ~Filters.command, ask_soyad),
                CallbackQueryHandler(cancel_ad_soyad, pattern='^cancel_ad_soyad$')
            ],
            ASK_SOYAD: [
                MessageHandler(Filters.text & ~Filters.command, ask_il),
                CallbackQueryHandler(ask_il, pattern='^skip_soyad$'),
                CallbackQueryHandler(cancel_ad_soyad, pattern='^cancel_ad_soyad$')
            ],
            ASK_IL: [
                MessageHandler(Filters.text & ~Filters.command, ask_ilce),
                CallbackQueryHandler(ask_ilce, pattern='^skip_il$'),
                CallbackQueryHandler(cancel_ad_soyad, pattern='^cancel_ad_soyad$')
            ],
            ASK_ILCE: [
                MessageHandler(Filters.text & ~Filters.command, complete_ad_soyad_query),
                CallbackQueryHandler(complete_ad_soyad_query, pattern='^skip_ilce$'),
                CallbackQueryHandler(cancel_ad_soyad, pattern='^cancel_ad_soyad$')
            ]
        },
        fallbacks=[CallbackQueryHandler(cancel_ad_soyad, pattern='^cancel_ad_soyad$')]
    )

    dp.add_handler(ad_soyad_handler)
    dp.add_handler(CallbackQueryHandler(handle_query_selection, pattern='^(tc_normal|tc_pro|adres|hane|aile|gsm_tc|gsm_tc_pro|tc_gsm|tc_gsm_pro|operator|sulale|sulale_pro|hayat_hikayesi|isyeri|isyeri_arkadasi|isyeri_yetkili)$'))
    dp.add_handler(CallbackQueryHandler(show_free_menu, pattern='^free_menu$'))
    dp.add_handler(CallbackQueryHandler(show_premium_menu, pattern='^premium_menu$'))
    dp.add_handler(CallbackQueryHandler(start, pattern='^main_menu$'))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_error_handler(error_handler)

    updater.start_polling()
    logger.info("🤖 Bot başarıyla başlatıldı!")
    updater.idle()

if __name__ == '__main__':
    main()