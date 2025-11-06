#!/usr/bin/env python3
"""
Dashboard Simple para el Jefe - Control de Descuadres de Stock
Tecnobox Chile - Análisis de Supervisión
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Configuración de página
st.set_page_config(
    page_title="Control de Stock - Tecnobox Chile",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_stock_data():
    """Carga los datos de descuadres de stock"""
    
    def process_carahue1():
        df = pd.read_excel("Stock_Carahue1.xlsx", header=0)
        new_columns = df.iloc[0].values
        df.columns = new_columns
        df = df.iloc[1:].reset_index(drop=True)
        df.columns = [str(col).strip() for col in df.columns]
        
        column_mapping = {
            'Producto': 'producto',
            'Codigo': 'codigo',
            'Stock fisico': 'stock_real',
            'Stock ERP': 'stock_sistema', 
            'Diferencia': 'descuadre',
            'Precio Unitario': 'precio'
        }
        
        df.rename(columns=column_mapping, inplace=True)
        df = df.dropna(subset=['producto'])
        df['codigo'] = df['codigo'].astype(str)
        df['stock_real'] = pd.to_numeric(df['stock_real'], errors='coerce')
        df['stock_sistema'] = pd.to_numeric(df['stock_sistema'], errors='coerce')
        df['descuadre'] = pd.to_numeric(df['descuadre'], errors='coerce')
        df['precio'] = pd.to_numeric(df['precio'], errors='coerce')
        
        df['productos_faltantes'] = abs(df['descuadre'])
        df['perdida_dinero'] = df['productos_faltantes'] * df['precio']
        
        return df

    def process_carahue2():
        df = pd.read_excel("stock carahue 2.xlsx", header=0)
        new_columns = df.iloc[0].values
        df.columns = new_columns
        df = df.iloc[1:].reset_index(drop=True)
        df.columns = [str(col).strip() for col in df.columns]
        
        column_mapping = {
            'Producto': 'producto',
            'Codigo': 'codigo',
            'Stock fisico': 'stock_real',
            'Stock Sistema': 'stock_sistema',
            'Diferencia': 'descuadre',
            'Precio': 'precio',
            'Perdida': 'perdida_dinero'
        }
        
        df.rename(columns=column_mapping, inplace=True)
        df = df.dropna(subset=['producto'])
        df['codigo'] = df['codigo'].astype(str)
        df['stock_real'] = pd.to_numeric(df['stock_real'], errors='coerce')
        df['stock_sistema'] = pd.to_numeric(df['stock_sistema'], errors='coerce')
        df['descuadre'] = pd.to_numeric(df['descuadre'], errors='coerce')
        df['precio'] = pd.to_numeric(df['precio'], errors='coerce')
        df['perdida_dinero'] = pd.to_numeric(df['perdida_dinero'], errors='coerce')
        
        df['productos_faltantes'] = abs(df['descuadre'])
        
        return df
    
    c1_data = process_carahue1()
    c2_data = process_carahue2()
    
    return c1_data, c2_data

# Cargar datos
df_c1, df_c2 = load_stock_data()

# Título principal
st.title("CONTROL DE STOCK - TECNOBOX CHILE")
st.markdown("### Análisis de Descuadres y Supervisión de Inventario")

# Resumen general
col1, col2, col3 = st.columns(3)

with col1:
    total_productos_c1 = len(df_c1)
    perdida_c1 = df_c1['perdida_dinero'].sum()
    st.metric(
        label="CARAHUE 1",
        value=f"{total_productos_c1} productos con problemas",
        delta=f"Pérdida: ${perdida_c1:,.0f}"
    )

with col2:
    total_productos_c2 = len(df_c2)
    perdida_c2 = df_c2['perdida_dinero'].sum()
    st.metric(
        label="CARAHUE 2", 
        value=f"{total_productos_c2} productos con problemas",
        delta=f"Pérdida: ${perdida_c2:,.0f}"
    )

with col3:
    perdida_total = perdida_c1 + perdida_c2
    total_productos = total_productos_c1 + total_productos_c2
    st.metric(
        label="IMPACTO TOTAL",
        value=f"${perdida_total:,.0f}",
        delta=f"{total_productos} productos afectados",
        delta_color="inverse"
    )

st.markdown("---")

# Tabs para cada sucursal
tab1, tab2, tab3 = st.tabs(["CARAHUE 1 - DETALLE COMPLETO", "CARAHUE 2 - DETALLE COMPLETO", "PRODUCTOS CRÍTICOS"])

with tab1:
    st.header(f"SUCURSAL CARAHUE 1")
    
    # Métricas específicas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Productos Afectados", f"{len(df_c1)}")
    with col2:
        st.metric("Pérdida Total", f"${df_c1['perdida_dinero'].sum():,.0f}")
    with col3:
        promedio_perdida = df_c1['perdida_dinero'].mean()
        st.metric("Pérdida Promedio por Producto", f"${promedio_perdida:,.0f}")
    
    st.subheader(" Productos Más Críticos (Mayor Pérdida)")
    top_c1 = df_c1.nlargest(10, 'perdida_dinero')[['producto', 'codigo', 'productos_faltantes', 'precio', 'perdida_dinero']]
    top_c1_display = top_c1.copy()
    top_c1_display.columns = ['Producto', 'Código', 'Unidades Faltantes', 'Precio Unitario', 'Pérdida en Pesos']
    top_c1_display['Precio Unitario'] = top_c1_display['Precio Unitario'].apply(lambda x: f"${x:,.0f}")
    top_c1_display['Pérdida en Pesos'] = top_c1_display['Pérdida en Pesos'].apply(lambda x: f"${x:,.0f}")
    
    st.dataframe(top_c1_display, width='stretch', hide_index=True)
    
    st.subheader(" Gráfico de Impacto Financiero")
    if len(top_c1) > 0:
        fig = px.bar(
            top_c1.head(8), 
            x='perdida_dinero', 
            y='producto',
            orientation='h',
            title="Top 8 Productos con Mayor Pérdida - Carahue 1",
            labels={'perdida_dinero': 'Pérdida en Pesos', 'producto': 'Productos'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, width='stretch')
    
    st.subheader(" LISTA COMPLETA DE DESCUADRES - CARAHUE 1")
    df_c1_completo = df_c1[['producto', 'codigo', 'stock_real', 'stock_sistema', 'productos_faltantes', 'precio', 'perdida_dinero']].copy()
    df_c1_completo.columns = ['Producto', 'Código', 'Stock Real', 'Stock Sistema', 'Faltantes', 'Precio', 'Pérdida Total']
    df_c1_completo = df_c1_completo.sort_values('Pérdida Total', ascending=False)
    
    # Formatear moneda
    df_c1_completo['Precio'] = df_c1_completo['Precio'].apply(lambda x: f"${x:,.0f}")
    df_c1_completo['Pérdida Total'] = df_c1_completo['Pérdida Total'].apply(lambda x: f"${x:,.0f}")
    
    st.dataframe(df_c1_completo, width='stretch', hide_index=True)

with tab2:
    st.header(f" SUCURSAL CARAHUE 2")
    
    # Métricas específicas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Productos Afectados", f"{len(df_c2)}")
    with col2:
        st.metric("Pérdida Total", f"${df_c2['perdida_dinero'].sum():,.0f}")
    with col3:
        promedio_perdida = df_c2['perdida_dinero'].mean()
        st.metric("Pérdida Promedio por Producto", f"${promedio_perdida:,.0f}")
    
    st.subheader(" Productos Más Críticos (Mayor Pérdida)")
    top_c2 = df_c2.nlargest(10, 'perdida_dinero')[['producto', 'codigo', 'productos_faltantes', 'precio', 'perdida_dinero']]
    top_c2_display = top_c2.copy()
    top_c2_display.columns = ['Producto', 'Código', 'Unidades Faltantes', 'Precio Unitario', 'Pérdida en Pesos']
    top_c2_display['Precio Unitario'] = top_c2_display['Precio Unitario'].apply(lambda x: f"${x:,.0f}")
    top_c2_display['Pérdida en Pesos'] = top_c2_display['Pérdida en Pesos'].apply(lambda x: f"${x:,.0f}")
    
    st.dataframe(top_c2_display, width='stretch', hide_index=True)
    
    st.subheader(" Gráfico de Impacto Financiero")
    if len(top_c2) > 0:
        fig = px.bar(
            top_c2.head(8), 
            x='perdida_dinero', 
            y='producto',
            orientation='h',
            title="Top 8 Productos con Mayor Pérdida - Carahue 2",
            labels={'perdida_dinero': 'Pérdida en Pesos', 'producto': 'Productos'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, width='stretch')
    
    st.subheader(" LISTA COMPLETA DE DESCUADRES - CARAHUE 2")
    df_c2_completo = df_c2[['producto', 'codigo', 'stock_real', 'stock_sistema', 'productos_faltantes', 'precio', 'perdida_dinero']].copy()
    df_c2_completo.columns = ['Producto', 'Código', 'Stock Real', 'Stock Sistema', 'Faltantes', 'Precio', 'Pérdida Total']
    df_c2_completo = df_c2_completo.sort_values('Pérdida Total', ascending=False)
    
    # Formatear moneda
    df_c2_completo['Precio'] = df_c2_completo['Precio'].apply(lambda x: f"${x:,.0f}")
    df_c2_completo['Pérdida Total'] = df_c2_completo['Pérdida Total'].apply(lambda x: f"${x:,.0f}")
    
    st.dataframe(df_c2_completo, width='stretch', hide_index=True)

with tab3:
    st.header(" PRODUCTOS CRÍTICOS - PROBLEMAS EN AMBAS SUCURSALES")
    
    codes_c1 = set(df_c1['codigo'].astype(str))
    codes_c2 = set(df_c2['codigo'].astype(str))
    critical_codes = codes_c1 & codes_c2
    
    if len(critical_codes) > 0:
        st.error(f" ALERTA: {len(critical_codes)} productos tienen problemas en AMBAS sucursales")
        st.markdown("**Esto indica problemas sistemáticos de supervisión y control**")
        
        critical_data = []
        
        for code in critical_codes:
            producto_c1 = df_c1[df_c1['codigo'].astype(str) == code]
            producto_c2 = df_c2[df_c2['codigo'].astype(str) == code]
            
            if len(producto_c1) > 0 and len(producto_c2) > 0:
                p1 = producto_c1.iloc[0]
                p2 = producto_c2.iloc[0]
                
                # Verificar que no haya valores NaN
                if pd.notna(p1['perdida_dinero']) and pd.notna(p2['perdida_dinero']):
                    critical_data.append({
                        'Producto': str(p1['producto']),
                        'Código': str(code),
                        'Faltantes C1': f"{p1['productos_faltantes']:.0f} unid.",
                        'Pérdida C1': f"${p1['perdida_dinero']:,.0f}",
                        'Faltantes C2': f"{p2['productos_faltantes']:.0f} unid.",
                        'Pérdida C2': f"${p2['perdida_dinero']:,.0f}",
                        'Pérdida Total': f"${p1['perdida_dinero'] + p2['perdida_dinero']:,.0f}"
                    })
        
        if critical_data:
            critical_df = pd.DataFrame(critical_data)
            critical_df = critical_df.sort_values('Pérdida Total', ascending=False)
            st.dataframe(critical_df, width='stretch', hide_index=True)
            
            # Resumen de productos críticos
            total_critico = 0
            for code in critical_codes:
                producto_c1 = df_c1[df_c1['codigo'].astype(str) == code]
                producto_c2 = df_c2[df_c2['codigo'].astype(str) == code]
                
                if len(producto_c1) > 0 and len(producto_c2) > 0:
                    p1 = producto_c1.iloc[0]
                    p2 = producto_c2.iloc[0]
                    
                    if pd.notna(p1['perdida_dinero']) and pd.notna(p2['perdida_dinero']):
                        total_critico += p1['perdida_dinero'] + p2['perdida_dinero']
            
            st.metric(
                "Pérdida Total en Productos Críticos", 
                f"${total_critico:,.0f}",
                help="Productos que faltan en ambas sucursales - Indica fallas de supervisión"
            )
        
    else:
        st.success(" No hay productos con problemas simultáneos en ambas sucursales")

# Análisis de supervisión al final
st.markdown("---")
st.header(" ANÁLISIS DE SUPERVISIÓN")

col1, col2 = st.columns(2)

with col1:
    st.subheader(" Comparación de Desempeño")
    
    # Crear gráfico comparativo
    comparison_data = pd.DataFrame({
        'Sucursal': ['Carahue 1', 'Carahue 2'],
        'Productos con Problemas': [len(df_c1), len(df_c2)],
        'Pérdida Total': [df_c1['perdida_dinero'].sum(), df_c2['perdida_dinero'].sum()]
    })
    
    fig = px.bar(
        comparison_data, 
        x='Sucursal', 
        y='Pérdida Total',
        title="Comparación de Pérdidas por Sucursal",
        text='Pérdida Total'
    )
    fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    st.plotly_chart(fig, width='stretch')

with col2:
    st.subheader(" Indicadores de Control")
    
    if len(df_c2) > len(df_c1):
        peor_sucursal = "Carahue 2"
        diferencia = len(df_c2) - len(df_c1)
    else:
        peor_sucursal = "Carahue 1" 
        diferencia = len(df_c1) - len(df_c2)
    
    st.warning(f" **{peor_sucursal}** tiene {diferencia} productos más con problemas")
    
    perdida_promedio_c1 = df_c1['perdida_dinero'].mean()
    perdida_promedio_c2 = df_c2['perdida_dinero'].mean()
    
    if perdida_promedio_c2 > perdida_promedio_c1:
        diferencia_promedio = perdida_promedio_c2 - perdida_promedio_c1
        st.error(f"**Carahue 2** tiene mayor pérdida promedio por producto: ${perdida_promedio_c2:,.0f} (${diferencia_promedio:,.0f} más que Carahue 1)")
    else:
        diferencia_promedio = perdida_promedio_c1 - perdida_promedio_c2
        st.error(f"**Carahue 1** tiene mayor pérdida promedio por producto: ${perdida_promedio_c1:,.0f} (${diferencia_promedio:,.0f} más que Carahue 2)")
    
    productos_criticos = len(critical_codes)
    if productos_criticos > 0:
        st.error(f" **{productos_criticos} productos críticos** indican fallas sistemáticas de supervisión")

st.info(" **Recomendación:** Los descuadres mostrados requieren revisión inmediata de los procesos de supervisión y control de inventario.")