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
kubectl create secret generic dynatrace-otelcol-dt-api-credentials --from-literal=DT_ENDPOINT=https://xxxx.com/api/v2/otlp --from-literal=DT_API_TOKEN=TOKEN -n dynatarce
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm repo update
helm upgrade -i dynatrace-collector open-telemetry/opentelemetry-collector -f kubernetes/values-deployment.yaml -n dynatrace
```

### 3.2. Verificar los Recursos en Kubernetes

```bash
kubectl get pods,svc -n dynatrace
```

---

## 4. Probar la Implementación

### 4.1. Acceder a la User Interface y robar el API de Inventario

```bash
curl --location --request GET 'http://<EXTERNAL-IP>'
# {"message":"Bienvenido al User Interface Microservice"}

```

```bash
curl --location --request POST 'http://<EXTERNAL-IP>/add_item?name=batery&quantity=20000'
# {"message":"Item agregado correctamente","data":{"message":"Item 'batery' agregado con cantidad 20000"}}

```

```bash
curl --location --request GET 'http://<EXTERNAL-IP>/items/'
# {"items":[{"id":1,"name":"Laptop","quantity":10},{"id":2,"name":"Mouse","quantity":50},{"id":3,"name":"Teclado","quantity":30},{"id":4,"name":"arduino","quantity":40}, .......
```
---

## 5. Verificar Trazas en Dynatrace

Accede a tu **Dynatrace** e ingresa a la sección de **trazas** o **PurePath**.

---

¡Con esto has completado el despliegue de los microservicios instrumentados con **OpenTelemetry** y la configuración del **Dynatrace OpenTelemetry Collector**!

