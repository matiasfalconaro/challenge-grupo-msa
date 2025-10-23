#!/bin/bash
set -e

# APP CONFIG
PROJECT_NAME="Sistema D'Hondt"
PORT_FRONTEND=3000
PORT_BACKEND=5000
PORT_DATABASE=5432
ENV_FILE=".env"
COMPOSE_DEV_FILE="docker-compose.dev.yaml"
COMPOSE_PRD_FILE="docker-compose.prd.yaml"

# DOCKERHUB CONFIG
DOCKERHUB_NAMESPACE="mlfalconaro"
PROJECT_PREFIX="challenge-grupo-msa"

# COLORS
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

# HELPER FUNCTIONS
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error()   { echo -e "${RED}✗ $1${NC}"; }
print_info()    { echo -e "${CYAN}ℹ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_step()    { echo -e "${BLUE}→ $1${NC}"; }
print_header() {
    echo ""
    echo -e "${CYAN}======================================${NC}"
    echo -e "  $1"
    echo -e "${CYAN}======================================${NC}"
    echo ""
}

get_compose_cmd() {
    if docker compose version &> /dev/null 2>&1; then
        echo "docker compose"
    else
        echo "docker-compose"
    fi
}

get_compose_file() {
    local mode="${1:-dev}"
    if [ "$mode" = "prd" ]; then
        echo "$COMPOSE_PRD_FILE"
    else
        echo "$COMPOSE_DEV_FILE"
    fi
}

check_env_file() {
    local mode="$1"
    if [ ! -f "$ENV_FILE" ]; then
        print_error "Archivo de entorno '$ENV_FILE' no encontrado"
        if [ "$mode" = "prd" ]; then
            print_info "En producción, asegúrate de tener configuradas todas las variables de entorno"
        else
            print_info "Crea el archivo .env basado en .env.example"
        fi
        exit 1
    fi
}

check_docker_login() {
    if ! docker system info > /dev/null 2>&1; then
        print_error "Docker no está ejecutándose o no tienes permisos"
        exit 1
    fi

    if ! docker info 2>/dev/null | grep -q "Username"; then
        print_warning "No estás logueado en DockerHub"
        print_info "Ejecuta: docker login -u $DOCKERHUB_NAMESPACE"
        echo ""
        read -p "¿Quieres intentar loguearte ahora? (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker login -u "$DOCKERHUB_NAMESPACE"
        else
            print_error "Debes estar logueado en DockerHub para hacer push"
            exit 1
        fi
    fi
}

get_image_name() {
    local service="$1"
    local tag="${2:-latest}"
    echo "$DOCKERHUB_NAMESPACE/$PROJECT_PREFIX-$service:$tag"
}

# MAIN FUNCTIONS
compose_up() {
    local mode="${1:-dev}"
    local file=$(get_compose_file "$mode")
    local cmd=$(get_compose_cmd)
    
    check_env_file "$mode"
    
    print_info "Usando compose file: $file"
    $cmd --env-file "$ENV_FILE" -f "$file" up -d
}

compose_down() {
    local mode="${1:-dev}"
    local file=$(get_compose_file "$mode")
    local cmd=$(get_compose_cmd)
    $cmd --env-file "$ENV_FILE" -f "$file" down
}

compose_build() {
    local mode="${1:-dev}"
    local file=$(get_compose_file "$mode")
    local cmd=$(get_compose_cmd)
    $cmd --env-file "$ENV_FILE" -f "$file" build
}

compose_logs() {
    local mode="${1:-dev}"
    shift
    local service="$1"
    local file=$(get_compose_file "$mode")
    local cmd=$(get_compose_cmd)

    if [ -z "$service" ]; then
        $cmd --env-file "$ENV_FILE" -f "$file" logs -f --tail=50
    else
        $cmd --env-file "$ENV_FILE" -f "$file" logs -f --tail=50 "$service"
    fi
}

compose_ps() {
    local mode="${1:-dev}"
    local file=$(get_compose_file "$mode")
    local cmd=$(get_compose_cmd)
    $cmd --env-file "$ENV_FILE" -f "$file" ps
}

wait_for_services() {
    local mode="$1"
    print_info "Esperando a que los servicios estén listos..."

    print_info "Esperando por PostgreSQL..."
    timeout 60s bash -c "until docker exec dhondt-postgres pg_isready -U \$POSTGRES_USER -d \$POSTGRES_DB; do sleep 2; done" || {
        print_error "PostgreSQL no está respondiendo"
        return 1
    }

    if [ "$mode" = "dev" ]; then
        print_info "Esperando por Backend..."
        timeout 30s bash -c "until curl -f http://localhost:$PORT_BACKEND/health >/dev/null 2>&1; do sleep 2; done" || {
            print_warning "Backend tarda en responder, continuando..."
        }
    fi

    print_success "Servicios listos"
}

# DOCKERHUB FUNCTIONS
build_and_tag() {
    local service="$1"
    local tag="${2:-latest}"
    local context="$3"
    local dockerfile="${4:-Dockerfile}"

    print_step "Construyendo $service..."
    docker build -t $(get_image_name "$service" "$tag") -f "$context/$dockerfile" "$context"
    print_success "Imagen $service construida y taggeada: $(get_image_name "$service" "$tag")"
}

tag_image() {
    local service="$1"
    local source_tag="${2:-latest}"
    local target_tag="$3"

    local source_image=$(get_image_name "$service" "$source_tag")
    local target_image=$(get_image_name "$service" "$target_tag")

    print_step "Taggeando $service: $source_tag → $target_tag"
    docker tag "$source_image" "$target_image"
    print_success "Imagen taggeada: $target_image"
}

push_image() {
    local service="$1"
    local tag="${2:-latest}"

    local image=$(get_image_name "$service" "$tag")

    print_step "Haciendo push de $service:$tag..."
    docker push "$image"
    print_success "Push completado: $image"
}

build_all() {
    local tag="${1:-latest}"

    print_header "Construyendo todas las imágenes (tag: $tag)"
    check_docker_login

    print_step "Construyendo backend..."
    build_and_tag "backend" "$tag" "./backend"

    print_step "Construyendo frontend..."
    build_and_tag "frontend" "$tag" "./frontend"

    print_step "Construyendo postgres..."
    build_and_tag "postgres" "$tag" "./database"

    print_success "Todas las imágenes construidas y taggeadas con: $tag"
}

tag_all() {
    local source_tag="${1:-latest}"
    local target_tag="$2"

    if [ -z "$target_tag" ]; then
        print_error "Debes especificar el tag destino"
        echo "Uso: ./run.sh tag-all <source-tag> <target-tag>"
        exit 1
    fi

    print_header "Taggeando todas las imágenes: $source_tag → $target_tag"

    for service in backend frontend postgres; do
        tag_image "$service" "$source_tag" "$target_tag"
    done

    print_success "Todas las imágenes taggeadas: $source_tag → $target_tag"
}

push_all() {
    local tag="${1:-latest}"

    print_header "Haciendo push de todas las imágenes (tag: $tag)"
    check_docker_login

    for service in backend frontend postgres; do
        push_image "$service" "$tag"
    done

    print_success "Todas las imágenes pusheadas a DockerHub"
}

release() {
    local version="${1:-latest}"

    print_header "Lanzando versión: $version"
    check_docker_login

    build_all "$version"

    if [ "$version" != "latest" ]; then
        print_step "Taggeando también como 'latest'"
        tag_all "$version" "latest"
        push_all "latest"
    fi

    push_all "$version"

    print_success "Release $version completada"
}

list_images() {
    print_header "Imágenes del proyecto en local"

    echo -e "${CYAN}Imágenes locales:${NC}"
    docker images | grep "$DOCKERHUB_NAMESPACE/$PROJECT_PREFIX-" | head -10

    echo ""
    echo -e "${CYAN}Tags disponibles para cada servicio:${NC}"
    for service in backend frontend postgres; do
        echo -e "${GREEN}$service:${NC}"
        docker images --format "table {{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" \
            | grep "$DOCKERHUB_NAMESPACE/$PROJECT_PREFIX-$service" \
            | sort -r || echo "  No hay imágenes locales"
    done
}

# CLI COMMANDS
start() {
    local mode="${1:-dev}"
    print_header "Iniciando servicios ($mode)"

    if compose_up "$mode"; then
        wait_for_services "$mode"
        print_success "Todos los servicios se iniciaron correctamente"
        show_urls "$mode"
    else
        print_error "Error al iniciar los servicios"
        exit 1
    fi
}

stop() {
    local mode="${1:-dev}"
    print_header "Deteniendo servicios ($mode)"
    if compose_down "$mode"; then
        print_success "Todos los servicios se detuvieron correctamente"
    else
        print_error "Error al detener los servicios"
        exit 1
    fi
}

restart() {
    local mode="${1:-dev}"
    print_header "Reiniciando servicios ($mode)"
    stop "$mode"
    start "$mode"
}

build() {
    local mode="${1:-dev}"
    print_header "Construyendo e iniciando servicios ($mode)"
    print_info "Construyendo imágenes de Docker..."
    if compose_build "$mode"; then
        print_success "Construcción completada"
    else
        print_error "Error durante la construcción"
        exit 1
    fi
    print_info "Iniciando servicios..."
    start "$mode"
}

rebuild() {
    local mode="${1:-dev}"
    print_header "Reconstruyendo servicios ($mode)"
    print_info "Reconstruyendo imágenes de Docker..."
    if compose_build "$mode"; then
        print_success "Reconstrucción completada"
    else
        print_error "Error durante la reconstrucción"
        exit 1
    fi
    print_info "Reiniciando servicios..."
    start "$mode"
}

logs() {
    local mode="${1:-dev}"
    local service="$2"
    print_header "Mostrando logs ($mode - $service)"
    compose_logs "$mode" "$service"
}

status() {
    local mode="${1:-dev}"
    print_header "Estado de los servicios ($mode)"
    compose_ps "$mode"
    echo ""
    show_urls "$mode"
}

clean() {
    print_header "Limpiando entorno"
    echo -e "${YELLOW}ADVERTENCIA: Esto eliminará:${NC}"
    echo "  - Todos los contenedores"
    echo "  - Todos los volúmenes (se perderán los datos de la base)"
    echo "  - Todas las imágenes construidas"
    echo ""
    echo -e "${YELLOW}Presione Ctrl+C para cancelar, o Enter para continuar...${NC}"
    read

    local mode="${1:-dev}"
    compose_down "$mode" -v

    print_info "Eliminando imágenes construidas..."
    docker images | grep "dhondt-" | awk '{print $3}' | xargs docker rmi -f 2>/dev/null || true
    docker images | grep "$DOCKERHUB_NAMESPACE/$PROJECT_PREFIX-" | awk '{print $3}' | xargs docker rmi -f 2>/dev/null || true
    print_success "Entorno limpiado correctamente"
}

show_urls() {
    local mode="$1"
    echo ""
    echo -e "${GREEN}URLs de los servicios ($mode):${NC}"
    echo "  Frontend:    http://localhost:$PORT_FRONTEND"
    echo "  Backend:     http://localhost:$PORT_BACKEND"
    echo "  API Docs:    http://localhost:$PORT_BACKEND/docs"

    if [ -f "$ENV_FILE" ]; then
        source "$ENV_FILE"
        echo "  Base de datos: postgresql://${POSTGRES_USER}:****@localhost:$PORT_DATABASE/${POSTGRES_DB}"
    else
        echo "  Base de datos: postgresql://localhost:$PORT_DATABASE"
    fi

    if [ "$mode" = "prd" ]; then
        echo ""
        echo -e "${YELLOW}MODO PRODUCCIÓN:${NC}"
        echo "  - Usando imágenes pre-construidas de Docker Hub"
        echo "  - Backend healthcheck puede fallar sin curl instalado"
    else
        echo ""
        echo -e "${YELLOW}MODO DESARROLLO:${NC}"
        echo "  - Construyendo imágenes localmente"
        echo "  - Volúmenes persistentes para desarrollo"
    fi
    echo ""
}

show_help() {
    echo -e "
${CYAN}$PROJECT_NAME${NC}

${CYAN}USO:${NC}
  ./run.sh [COMANDO] [dev|prd|TAG] [SERVICIO|TAG]

${CYAN}COMANDOS PRINCIPALES:${NC}
  ${GREEN}start${NC}            Iniciar todos los servicios
  ${GREEN}stop${NC}             Detener todos los servicios
  ${GREEN}restart${NC}          Reiniciar todos los servicios
  ${GREEN}build${NC}            Construir imágenes desde cero e iniciar servicios
  ${GREEN}rebuild${NC}          Reconstruir imágenes (usa cache) y reiniciar servicios
  ${GREEN}logs${NC} [SERVICIO]  Seguir logs (todos los servicios o un servicio específico)
  ${GREEN}status${NC}           Mostrar estado de servicios y URLs
  ${GREEN}clean${NC}            Eliminar contenedores, volúmenes e imágenes

${CYAN}COMANDOS DOCKERHUB:${NC}
  ${GREEN}build-all${NC} [TAG]  Construir todas las imágenes con tag específico
  ${GREEN}tag-all${NC} <src> <dst>  Taggear todas las imágenes de un tag a otro
  ${GREEN}push-all${NC} [TAG]   Hacer push de todas las imágenes con tag específico
  ${GREEN}release${NC} [VER]    Construir, taggear y hacer push de una versión
  ${GREEN}images${NC}           Listar imágenes locales del proyecto

${CYAN}MODOS:${NC}
  ${GREEN}dev${NC}              Desarrollo (construcción local)
  ${GREEN}prd${NC}              Producción (imágenes de Docker Hub)

${CYAN}EJEMPLOS:${NC}
  ./run.sh start dev            # Iniciar servicios de desarrollo
  ./run.sh start prd            # Iniciar servicios de producción  
  ./run.sh logs backend dev     # Ver logs del backend en dev
  ./run.sh rebuild prd          # Reconstruir servicios de producción
  
  ${CYAN}# DockerHub examples:${NC}
  ./run.sh build-all v1.0.0     # Construir imágenes con tag v1.0.0
  ./run.sh tag-all v1.0.0 latest # Taggear v1.0.0 como latest
  ./run.sh push-all v1.0.0      # Hacer push de tag v1.0.0
  ./run.sh release v2.0.0       # Lanzar versión v2.0.0
  ./run.sh images               # Listar imágenes locales
"
}

# MAIN
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    cmd="$1"
    arg1="${2:-}"
    arg2="${3:-}"

    case "$cmd" in
        start)    start "$arg1" ;;
        stop)     stop "$arg1" ;;
        restart)  restart "$arg1" ;;
        build)    build "$arg1" ;;
        rebuild)  rebuild "$arg1" ;;
        logs)     logs "$arg1" "$arg2" ;;
        status)   status "$arg1" ;;
        clean)    clean "$arg1" ;;
        build-all) build_all "$arg1" ;;
        tag-all)   tag_all "$arg1" "$arg2" ;;
        push-all)  push_all "$arg1" ;;
        release)   release "$arg1" ;;
        images)    list_images ;;

        help|--help|-h) show_help ;;
        *) 
            print_error "Comando desconocido: $cmd"
            echo "Ejecute './run.sh help' para ver los comandos disponibles"
            exit 1
            ;;
    esac
}

main "$@"
