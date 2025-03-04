# Guía Completa: Despliegue de Microservicios con Instrumentación Automática (OTEL) y Dynatrace

Esta guía describe los pasos necesarios para construir, desplegar y probar un conjunto de microservicios instrumentados automáticamente con **OpenTelemetry (OTEL)**, así como para configurar y desplegar el **Dynatrace OpenTelemetry Collector** en un clúster de Kubernetes.

---

## Índice

1. **Construcción y Publicación de Imágenes Docker**  
   1.1 [Construir las imágenes Docker](#11-construir-las-imágenes-docker)  
   1.2 [Etiquetar y subir las imágenes al registro](#12-etiquetar-y-subir-las-imágenes-al-registro)  

2. **Desplegar los Microservicios en Kubernetes**  
   2.1 [Aplicar el YAML de Kubernetes](#21-aplicar-el-yaml-de-kubernetes)  
   2.2 [Verificar los Recursos en Kubernetes](#22-verificar-los-recursos-en-kubernetes)  

3. **Desplegar Dynatrace OpenTelemetry Collector**  
   3.1 [Agregar el repositorio Helm y desplegar el Collector](#31-agregar-el-repositorio-helm-y-desplegar-el-collector)  
   3.2 [Verificar los Recursos en Kubernetes](#32-verificar-los-recursos-en-kubernetes)  

4. **Probar la Implementación**  
   4.1 [Acceder a la User Interface](#41-acceder-a-la-user-interface)  
   4.2 [Probar el API de Inventario](#42-probar-el-api-de-inventario)  

5. **Verificar Trazas en Dynatrace**

6. **Personalización Opcional**

---

## 1. Construcción y Publicación de Imágenes Docker

### 1.1. Construir las imágenes Docker

```bash
docker build -t otel-user-interface:automatica_otel -f user_interface/Dockerfile ./user_interface
docker build -t otel-api-inventario:automatica_otel -f api_inventario/Dockerfile ./api_inventario
docker build -t otel-inventario-db:automatica_otel -f inventario_db/Dockerfile ./inventario_db
```

### 1.2. Etiquetar y subir las imágenes al registro

```bash
docker tag otel-user-interface:automatica_otel myrepo/otel-user-interface:automatica_otel
docker tag otel-api-inventario:automatica_otel myrepo/otel-api-inventario:automatica_otel
docker tag otel-inventario-db:automatica_otel myrepo/otel-inventario-db:automatica_otel

docker push myrepo/otel-user-interface:automatica_otel
docker push myrepo/otel-api-inventario:automatica_otel
docker push myrepo/otel-inventario-db:automatica_otel
```

---

## 2. Desplegar los Microservicios en Kubernetes

### 2.1. Aplicar el YAML de Kubernetes

```bash
kubectl apply -f kubernetes/microservices.yaml
```

### 2.2. Verificar los Recursos en Kubernetes

```bash
kubectl get pods,svc -n pocotelpython
```

---

## 3. Desplegar Dynatrace OpenTelemetry Collector

### 3.1. Agregar el repositorio Helm y desplegar el Collector
antes de aplicar el deploy modificar el kubernetes/dynatrace_collector.yaml modificar:
- linea 13: [URL](https://docs.dynatrace.com/docs/shortlink/otel-getstarted-otlpexport#export-to-saas-and-activegate)
- linea 14: [Token](https://docs.dynatrace.com/docs/shortlink/otel-getstarted-otlpexport#authentication-export-to-activegate)

```bash
kubectl apply -f dynatrace_collector.yaml
```

### 3.2. Verificar los Recursos en Kubernetes

```bash
kubectl get pods,svc -n dynatrace
```

---

## 4. Probar la Implementación

### 4.1. Acceder a la User Interface

```bash
http://<EXTERNAL-IP>:80
```

### 4.2. Probar el API de Inventario

```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"name": "Laptop", "quantity": 10}' \
     http://<api-inventario-service>:8001/items/add
```

---

## 5. Verificar Trazas en Dynatrace

Accede a tu **Dynatrace** e ingresa a la sección de **trazas** o **PurePath**.

---

## 6. Personalización Opcional

Si deseas personalizar el Collector, edita `values-deployment.yaml` y ejecuta:

```bash
helm upgrade -i dynatrace-collector open-telemetry/opentelemetry-collector \
  -f values-deployment.yaml -n dynatrace
```

---

¡Con esto has completado el despliegue de los microservicios instrumentados con **OpenTelemetry** y la configuración del **Dynatrace OpenTelemetry Collector**!

