{{/*
Expand the name of the chart.
*/}}
{{- define "basic-webapp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "basic-webapp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "basic-webapp.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "basic-webapp.labels" -}}
helm.sh/chart: {{ include "basic-webapp.chart" . }}
{{ include "basic-webapp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "basic-webapp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "basic-webapp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "basic-webapp.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "basic-webapp.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Generate environment variables from values
*/}}
{{- define "basic-webapp.envVars" -}}
{{- range .Values.env }}
- name: {{ .name }}
  value: {{ .value | quote }}
{{- end }}
{{- end }}

{{/*
Generate config map volume mount if enabled
*/}}
{{- define "basic-webapp.configMapVolume" -}}
{{- if .Values.configMap.enabled }}
- name: config-volume
  mountPath: /etc/config
{{- end }}
{{- end }}

{{/*
Generate secret volume mount if enabled
*/}}
{{- define "basic-webapp.secretVolume" -}}
{{- if .Values.secret.enabled }}
- name: secret-volume
  mountPath: /etc/secret
  readOnly: true
{{- end }}
{{- end }}

{{/*
Generate persistence volume claim if enabled
*/}}
{{- define "basic-webapp.persistenceVolume" -}}
{{- if .Values.persistence.enabled }}
- name: data-volume
  mountPath: /data
{{- end }}
{{- end }}