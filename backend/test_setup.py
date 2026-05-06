#!/usr/bin/env python3
"""
Script de validación rápida del backend.
Usa para verificar que todo está configurado correctamente antes de testing manual.

Uso:
    python test_setup.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def check_imports():
    """Verifica que todos los imports funcionen"""
    print("🔍 Verificando imports...")
    
    try:
        from app.core.config import get_settings
        print("  ✓ app.core.config")
    except Exception as e:
        print(f"  ✗ app.core.config: {e}")
        return False
    
    try:
        from app.core.security import hash_password, verify_password, create_access_token
        print("  ✓ app.core.security")
    except Exception as e:
        print(f"  ✗ app.core.security: {e}")
        return False
    
    try:
        from app.db.models import Usuario, Rol, UsuarioRol
        print("  ✓ app.db.models")
    except Exception as e:
        print(f"  ✗ app.db.models: {e}")
        return False
    
    try:
        from app.modules.auth import router, AuthService
        print("  ✓ app.modules.auth")
    except Exception as e:
        print(f"  ✗ app.modules.auth: {e}")
        return False
    
    try:
        from app.main import app
        print("  ✓ app.main")
    except Exception as e:
        print(f"  ✗ app.main: {e}")
        return False
    
    return True


def check_config():
    """Verifica que la configuración esté correcta"""
    print("\n⚙️  Verificando configuración...")
    
    try:
        from app.core.config import get_settings
        settings = get_settings()
        
        print(f"  ✓ DATABASE_URL: {settings.database_url[:40]}...")
        print(f"  ✓ SECRET_KEY: {settings.secret_key[:20]}...")
        print(f"  ✓ JWT Algorithm: {settings.algorithm}")
        print(f"  ✓ Token expiration: {settings.access_token_expire_minutes} min")
        print(f"  ✓ CORS origins: {len(settings.cors_origins_list)} dominios")
        print(f"  ✓ DEBUG: {settings.debug}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error en configuración: {e}")
        return False


def check_database():
    """Verifica conexión a base de datos"""
    print("\n🗄️  Verificando base de datos...")
    
    try:
        from sqlalchemy import text
        from app.db.base import engine
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("  ✓ Conexión a PostgreSQL OK")
        
        return True
    except Exception as e:
        print(f"  ✗ Error de conexión: {e}")
        print("    → Asegurate de que docker-compose está running: docker-compose up -d")
        return False


def check_security():
    """Verifica funciones de seguridad"""
    print("\n🔒 Verificando seguridad...")
    
    try:
        from app.core.security import hash_password, verify_password, create_access_token, decode_token
        
        # Test password hashing
        test_password = "testpassword123"
        hashed = hash_password(test_password)
        
        if len(hashed) < 50:
            print(f"  ✗ Hash bcrypt muy corto: {len(hashed)} caracteres")
            return False
        
        print(f"  ✓ Password hashing: {len(hashed)} caracteres (bcrypt)")
        
        # Verify password
        if not verify_password(test_password, hashed):
            print(f"  ✗ Password verification falló")
            return False
        
        print(f"  ✓ Password verification OK")
        
        # Test JWT
        token = create_access_token({"sub": 1})
        if not token:
            print(f"  ✗ JWT creation failed")
            return False
        
        print(f"  ✓ JWT creation OK: {len(token)} caracteres")
        
        # Decode JWT
        payload = decode_token(token)
        if not payload or payload.get("sub") != 1:
            print(f"  ✗ JWT decode failed")
            return False
        
        print(f"  ✓ JWT decode OK: user_id={payload.get('sub')}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error de seguridad: {e}")
        return False


def check_models():
    """Verifica que los modelos SQLModel estén correctos"""
    print("\n📦 Verificando modelos...")
    
    try:
        from app.db.models import Usuario, Rol
        
        # Verificar que son SQLModel
        if not hasattr(Usuario, '__table__'):
            print(f"  ✗ Usuario no es un SQLModel valido")
            return False
        
        print(f"  ✓ Usuario model OK")
        
        if not hasattr(Rol, '__table__'):
            print(f"  ✗ Rol no es un SQLModel valido")
            return False
        
        print(f"  ✓ Rol model OK")
        
        return True
    except Exception as e:
        print(f"  ✗ Error en modelos: {e}")
        return False


def main():
    """Ejecuta todos los checks"""
    print("=" * 60)
    print("🧪 FOOD STORE API - Setup Validation")
    print("=" * 60)
    
    checks = [
        ("Imports", check_imports),
        ("Configuration", check_config),
        ("Security", check_security),
        ("Models", check_models),
        ("Database", check_database),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error en {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\nResultado: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 ¡Todo listo! Puedes iniciar el servidor:")
        print("   uvicorn app.main:app --reload")
        return 0
    else:
        print("\n⚠️  Hay problemas. Revisa los errores arriba.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
