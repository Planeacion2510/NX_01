#!/usr/bin/env python
"""
Verifica el estado de la base de datos y determina la estrategia de migración
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexusone.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line


def check_database_state():
    """
    Verifica el estado de la base de datos y retorna:
    - 'empty': Base de datos vacía
    - 'needs_sync': Tablas existen pero sin migraciones registradas
    - 'synced': Base de datos correctamente migrada
    """
    
    try:
        with connection.cursor() as cursor:
            # 1. Verificar si existe la tabla django_migrations
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'django_migrations'
            """)
            migrations_table_exists = cursor.fetchone()[0] > 0
            
            if not migrations_table_exists:
                return 'empty'
            
            # 2. Contar migraciones registradas
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            migrations_count = cursor.fetchone()[0]
            
            # 3. Contar tablas del sistema (no pg_*)
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                AND table_name NOT LIKE 'pg_%'
            """)
            tables_count = cursor.fetchone()[0]
            
            # 4. Verificar específicamente django_content_type
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_name = 'django_content_type'
            """)
            content_type_exists = cursor.fetchone()[0] > 0
            
            print(f"📊 Estado de BD:")
            print(f"   - Tabla django_migrations: {'✅ Existe' if migrations_table_exists else '❌ No existe'}")
            print(f"   - Migraciones registradas: {migrations_count}")
            print(f"   - Tablas totales: {tables_count}")
            print(f"   - django_content_type: {'✅ Existe' if content_type_exists else '❌ No existe'}")
            
            # Lógica de decisión
            if migrations_count == 0 and tables_count > 1:
                # Tablas existen pero no hay migraciones registradas
                return 'needs_sync'
            elif migrations_count == 0 and tables_count <= 1:
                # Base de datos vacía
                return 'empty'
            else:
                # Base de datos con migraciones
                return 'synced'
                
    except Exception as e:
        print(f"⚠️  Error al verificar BD: {e}")
        print(f"   Asumiendo base de datos nueva")
        return 'empty'


def run_migrations(strategy):
    """Ejecuta migraciones según la estrategia"""
    
    print("\n" + "="*50)
    
    if strategy == 'empty':
        print("🆕 BASE DE DATOS NUEVA")
        print("   Ejecutando migraciones normales...")
        print("="*50 + "\n")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        
    elif strategy == 'needs_sync':
        print("🔄 SINCRONIZACIÓN REQUERIDA")
        print("   Tablas existen pero sin registro de migraciones")
        print("   Usando --fake-initial para sincronizar...")
        print("="*50 + "\n")
        execute_from_command_line(['manage.py', 'migrate', '--fake-initial', '--noinput'])
        
    elif strategy == 'synced':
        print("✅ BASE DE DATOS SINCRONIZADA")
        print("   Aplicando nuevas migraciones si existen...")
        print("="*50 + "\n")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    
    print("\n" + "="*50)
    print("✅ Migraciones completadas exitosamente")
    print("="*50 + "\n")


def main():
    """Función principal"""
    print("\n" + "="*50)
    print("🔍 VERIFICANDO ESTADO DE BASE DE DATOS")
    print("="*50 + "\n")
    
    strategy = check_database_state()
    
    print(f"\n📋 Estrategia seleccionada: {strategy.upper()}")
    
    run_migrations(strategy)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())