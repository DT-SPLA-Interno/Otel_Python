**Guía Completa: Despliegue de Microservicios con Instrumentación Automática (OTEL) y Dynatrace**
-------------------------------------------------------------------------------------------------

Esta guía describe los pasos necesarios para construir, desplegar y probar un conjunto de microservicios instrumentados automáticamente con **OpenTelemetry (OTEL)**, así como para configurar y desplegar el **Dynatrace OpenTelemetry Collector** en un clúster de Kubernetes.

### **Índice**

1.  **Construcción de Imágenes Docker**1.1 [Construir las imágenes Docker de los microservicios](#_1.1_Construir_las)1.2 [Subir las imágenes al registro](#_1.2_Subir_las_imágenes)
    
2.  **Crear el Secreto en Kubernetes**
    
3.  **Desplegar Dynatrace OpenTelemetry Collector**3.1 [Aplicar el YAML de Kubernetes](#_3.1_Aplicar_el)3.2 [Verificar los Recursos en Kubernetes](#_3.2_Verificar_los_Recursos)
    
4.  **Desplegar los Microservicios en Kubernetes**4.1 [Aplicar el archivo YAML para los microservicios](#_4.1_Aplicar_el)4.2 [Verificar los Recursos de los Microservicios](#_4.2_Verificar_los_Recursos)
    
5.  **Probar la Implementación**5.1 [Acceder a la User Interface](#_5.1_Acceder_a)5.2 [Probar el API de Inventario](#_5.2_Probar_el)
    
6.  **Verificar Trazas en Dynatrace**
    
7.  **Personalización Opcional**
    

**1\. Construcción de Imágenes Docker**
---------------------------------------

### **1.1. Construir las imágenes Docker de los microservicios**

Los microservicios son:

*   **User Interface**
    
*   **API Inventario**
    
*   **Base de datos MySQL** (con script de inicialización)
    

En cada carpeta se encuentra un Dockerfile. Para construir las imágenes usando la etiqueta **otel** (referenciando la instrumentación automática), ejecuta:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   bashCopyEditdocker build -t otel/user-interface:latest -f user_interface/Dockerfile ./user_interface  docker build -t otel/api-inventario:latest -f api_inventario/Dockerfile ./api_inventario  docker build -t otel/inventario-db:latest -f inventario_db/Dockerfile ./inventario_db   `

### **1.2. Subir las imágenes al registro**

Una vez construidas, las imágenes pueden empujarse (push) a tu repositorio Docker (por ejemplo, DockerHub, Amazon ECR, Google Container Registry, etc.):

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   bashCopyEditdocker push otel/user-interface:latest  docker push otel/api-inventario:latest  docker push otel/inventario-db:latest   `

> **Nota:** Ajusta la referencia de imagen si usas un repositorio privado o especificas una ruta distinta(por ejemplo, myrepo.com/otel/user-interface:latest).

**2\. Crear el Secreto en Kubernetes**
--------------------------------------

Para almacenar la URL de Dynatrace y el token de acceso, crea un secreto en el namespace **dynatrace** (asegúrate de que exista el namespace o créalo si es necesario):

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   bashCopyEditkubectl create secret generic dynatrace-otelcol-dt-api-credentials \    --from-literal=OTEL_EXPORTER_OTLP_ENDPOINT="https://xxxxxxxxxx/api/v2/otlp/v1/traces" \    --from-literal=OTEL_EXPORTER_OTLP_TOKEN="Token_de_Dynatrace_aquí" \    -n dynatrace   `

*   Reemplaza OTEL\_EXPORTER\_OTLP\_ENDPOINT y OTEL\_EXPORTER\_OTLP\_TOKEN con tus valores reales.
    
*   El secreto almacenará los valores en texto plano (stringData). Kubernetes los convierte internamente a base64.
    

**3\. Desplegar Dynatrace OpenTelemetry Collector**
---------------------------------------------------

### **3.1. Aplicar el YAML de Kubernetes**

Utiliza el archivo dynatrace-otel-collector.yaml (o como lo hayas nombrado) para desplegar:

*   El Deployment del Collector
    
*   El ConfigMap con la configuración del Collector
    
*   El Service en el puerto 4317 (OTLP gRPC) y 4318 (OTLP HTTP)
    

Ejecuta:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   bashCopyEditkubectl apply -f dynatrace-otel-collector.yaml   `

### **3.2. Verificar los Recursos en Kubernetes**

Observa que el Pod y el Service estén funcionando:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   bashCopyEditkubectl get pods,svc -n dynatrace   `

**Posible resultado**:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   pgsqlCopyEditNAME                                         READY   STATUS    RESTARTS   AGE  pod/dynatrace-collector-xxxxxxxxxx-abcde     1/1     Running   0          30s  NAME                                         TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)            AGE  service/dynatrace-collector                  ClusterIP   10.96.0.1                4317/TCP,4318/TCP  30s   `

**4\. Desplegar los Microservicios en Kubernetes**
--------------------------------------------------

### **4.1. Aplicar el archivo YAML para los microservicios**

En el archivo microservices.yaml (o equivalente), tendrás los Deployments y Services de:

*   **user\_interface**
    
*   **api\_inventario**
    
*   **inventario\_db**
    

Aplica el archivo:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   bashCopyEditkubectl apply -f kubernetes/microservices.yaml   `

### **4.2. Verificar los Recursos de los Microservicios**

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   bashCopyEditkubectl get pods,svc -n pocotelpython   `

**Ejemplo**:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   pgsqlCopyEditNAME                                         READY   STATUS    RESTARTS   AGE  pod/user-interface-xxxxxx-abcde             1/1     Running   0          30s  pod/api-inventario-xxxxxx-abcde             1/1     Running   0          30s  pod/inventario-db-xxxxxx-abcde              1/1     Running   0          30s  NAME                                         TYPE          CLUSTER-IP   EXTERNAL-IP  PORT(S)      AGE  service/user-interface                       LoadBalancer  10.96.0.5           80:8000/TCP   30s  service/api-inventario                       ClusterIP     10.96.0.6           8001/TCP      30s  service/inventario-db                        ClusterIP     10.96.0.7           3306/TCP      30s   `

**5\. Probar la Implementación**
--------------------------------

### **5.1. Acceder a la User Interface**

Si tu Service para user-interface es de tipo LoadBalancer, obtén la IP o DNS asignado y visita en tu navegador:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   cppCopyEdithttp://:80   `

El endpoint raíz (/) debe responder con un mensaje de bienvenida. Además, tienes:

*   **/add\_item/** para agregar un ítem al inventario.
    
*   **/items/** para listar ítems del inventario.
    

### **5.2. Probar el API de Inventario**

*   bashCopyEditcurl -X POST \\ -H "Content-Type: application/json" \\ -d '{"name": "Laptop", "quantity": 10}' \\ http://:8001/items/addDebe responder con un mensaje confirmando la inserción.
    
*   bashCopyEditcurl http://:8001/items/allDebe retornar el JSON con la lista de ítems almacenados.
    

**6\. Verificar Trazas en Dynatrace**
-------------------------------------

Accede a tu **Dynatrace** e ingresa a la sección de **trazas** o **PurePath** (según la interfaz de Dynatrace). Deberías observar las trazas generadas por tus microservicios llegando a través del **Dynatrace OpenTelemetry Collector**.

**7\. Personalización Opcional**
--------------------------------

Si deseas personalizar el Collector (agregar **procesadores**, **otros exportadores**, **filtros**, etc.), edita la sección otel-collector-config.yaml en el ConfigMap. Luego, ejecuta:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   bashCopyEditkubectl apply -f dynatrace-otel-collector.yaml   `

para que el Collector se recargue con la nueva configuración.
