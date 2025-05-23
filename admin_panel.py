import streamlit as st
from database import get_all_users, ban_user, unban_user, update_premium
from datetime import datetime, timedelta
import time
import hashlib

# Oturum yönetimi için başlatıcı
def initialize_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'admin_username' not in st.session_state:
        st.session_state.admin_username = None

# Tüm Streamlit sürümleriyle uyumlu yenileme fonksiyonu
def safe_rerun():
    """Tüm Streamlit sürümleri için güvenli yenileme"""
    try:
        st.rerun()  # En yeni sürümler için
    except:
        try:
            st.experimental_rerun()  # Eski sürümler için
        except:
            pass  # Yenileme başarısız olursa sessizce devam et

# Şifre hashleme fonksiyonu
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def admin_login():
    st.sidebar.title("Admin Girişi")
    username = st.sidebar.text_input("Kullanıcı Adı", key="login_username")
    password = st.sidebar.text_input("Şifre", type="password", key="login_password")
    
    if st.sidebar.button("Giriş Yap", key="login_button"):
        # Örnek kimlik doğrulama (gerçek uygulamada veritabanı kullanın)
        if username == "admin" and hash_password(password) == hash_password("admin"):
            st.session_state.logged_in = True
            st.session_state.admin_username = username
            st.success("Başarıyla giriş yapıldı!")
            time.sleep(0.5)
            safe_rerun()
        else:
            st.sidebar.error("Hatalı kullanıcı adı veya şifre")

def show_admin_panel():
    st.title(f"Kullanıcı Yönetim Paneli - Hoş geldiniz, {st.session_state.admin_username}")
    
    # Çıkış butonu
    if st.sidebar.button("Çıkış Yap"):
        st.session_state.clear()  # Tüm oturumu temizle
        st.success("Başarıyla çıkış yapıldı!")
        time.sleep(0.5)
        safe_rerun()
    
    # Kullanıcı listesi
    users = get_all_users()
    if not users:
        st.warning("Veritabanında kullanıcı bulunamadı")
        return
    
    for user in users:
        user_id, username, first_name, last_name, is_premium, premium_end, is_banned, ban_reason = user
        
        # Kullanıcı bilgilerini düzenle
        display_name = f"{first_name or ''} {last_name or ''}".strip()
        display_name += f" (@{username})" if username and display_name else f"@{username}" if username else f"ID: {user_id}"
        
        with st.expander(display_name):
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.write(f"**ID:** {user_id}")
                status = "✅ Aktif" if not is_banned else f"❌ Yasaklı ({ban_reason or 'sebep belirtilmemiş'})"
                st.write(f"**Durum:** {status}")
                
                premium_active = is_premium and premium_end and (
                    datetime.strptime(premium_end, "%Y-%m-%d") > datetime.now() 
                    if isinstance(premium_end, str) else premium_end > datetime.now()
                )
                st.write(f"**Üyelik:** {'✅ Premium' if premium_active else '❌ Standart'}")
                if is_premium and premium_end:
                    st.write(f"**Bitiş Tarihi:** {premium_end}")
            
            with col2:
                # Yasağa alma/kaldırma işlemleri
                if is_banned:
                    if st.button(f"Yasağı Kaldır (ID: {user_id})"):
                        unban_user(user_id)
                        st.success("Yasak kaldırıldı!")
                        time.sleep(0.5)
                        safe_rerun()
                else:
                    # Yasaklama formu
                    with st.form(key=f"ban_form_{user_id}"):
                        reason = st.text_input(f"Yasaklama sebebi (ID: {user_id}):")
                        if st.form_submit_button("Yasakla"):
                            if reason:
                                ban_user(user_id, reason)
                                st.success("Kullanıcı yasaklandı!")
                                time.sleep(0.5)
                                safe_rerun()
                            else:
                                st.warning("Lütfen yasaklama sebebi girin")
                
                # Premium yönetimi için form
                with st.form(key=f"premium_form_{user_id}"):
                    col_add, col_remove = st.columns(2)
                    
                    with col_add:
                        days_to_add = st.number_input(
                            "Eklenecek Gün:", 
                            min_value=0, 
                            max_value=365, 
                            value=0, 
                            key=f"days_to_add_{user_id}"
                        )
                        if st.form_submit_button("Gün Ekle"):
                            if is_premium and premium_end:
                                current_end = datetime.strptime(premium_end, "%Y-%m-%d") if isinstance(premium_end, str) else premium_end
                                new_end = current_end + timedelta(days=days_to_add)
                            else:
                                new_end = datetime.now() + timedelta(days=days_to_add)
                            
                            update_premium(user_id, True, new_end.strftime("%Y-%m-%d"))
                            st.success(f"{days_to_add} gün eklendi! Yeni bitiş: {new_end.strftime('%Y-%m-%d')}")
                            time.sleep(0.5)
                            safe_rerun()
                    
                    with col_remove:
                        days_to_remove = st.number_input(
                            "Çıkarılacak Gün:", 
                            min_value=0, 
                            max_value=365, 
                            value=0, 
                            key=f"days_to_remove_{user_id}"
                        )
                        if st.form_submit_button("Gün Çıkar"):
                            if is_premium and premium_end:
                                current_end = datetime.strptime(premium_end, "%Y-%m-%d") if isinstance(premium_end, str) else premium_end
                                new_end = current_end - timedelta(days=days_to_remove)
                                
                                # Bugünden önceye ayarlama kontrolü
                                if new_end < datetime.now():
                                    new_end = datetime.now()
                                    st.warning("Gün çıkarıldı, premium bugün bitecek")
                                
                                update_premium(user_id, True, new_end.strftime("%Y-%m-%d"))
                                st.success(f"{days_to_remove} gün çıkarıldı! Yeni bitiş: {new_end.strftime('%Y-%m-%d')}")
                                time.sleep(0.5)
                                safe_rerun()
                            else:
                                st.warning("Bu kullanıcının premium üyeliği yok")

def main():
    st.set_page_config(page_title="Admin Paneli", layout="wide")
    initialize_session()
    
    if not st.session_state.logged_in:
        admin_login()
    else:
        show_admin_panel()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Bir hata oluştu: {str(e)}")
        time.sleep(2)
        safe_rerun()