#!/bin/bash
set -e

# APP CONFIG
PROJECT_NAME="Sistema D'Hondt"
PORT_FRONTEND=3000
PORT_BACKEND=5000
PORT_DATABASE=5432
ENV_FILE=".env"
COMPOSE_DEV_FILE="docker-compose.dev.yml"
COMPOSE_PRD_FILE="docker-compose.prd.yaml"

# COLORS
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# HEPER FUNCTIONS
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error()   { echo -e "${RED}✗ $1${NC}"; }
print_info()    { echo -e "${CYAN}ℹ $1${NC}"; }
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

# MAIN FUNCTIONS
compose_up() {
    local mode="${1:-dev}"
    local file=$(get_compose_file "$mode")
    local cmd=$(get_compose_cmd)
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

# CLI COMMANDS
start() {
    local mode="${1:-dev}"
    print_header "Iniciando servicios ($mode)"
    if compose_up "$mode"; then
        print_success "Todos los servicios se iniciaron correctamente"
        show_urls
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
    print_header "Mostrando logs ($service)"
    compose_logs "$mode" "$service"
}

status() {
    local mode="${1:-dev}"
    print_header "Estado de los servicios ($mode)"
    compose_ps "$mode"
    echo ""
    show_urls
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
    print_success "Entorno limpiado correctamente"
}

show_urls() {
    echo ""
    echo -e "${GREEN}URLs de los servicios:${NC}"
    echo "  Frontend:    http://localhost:$PORT_FRONTEND"
    echo "  Backend:     http://localhost:$PORT_BACKEND"
    echo "  API Docs:    http://localhost:$PORT_BACKEND/docs"
    echo "  Base de datos:    postgresql://\${POSTGRES_USER}:\${POSTGRES_PASSWORD}@postgres:5432/\${POSTGRES_DB}"
    echo ""
}

show_help() {
    echo -e "
${CYAN}$PROJECT_NAME${NC}

${CYAN}USO:${NC}
  ./run.sh [COMANDO] [dev|prd]

${CYAN}COMANDOS:${NC}
  ${GREEN}start${NC}            Iniciar todos los servicios
  ${GREEN}stop${NC}             Detener todos los servicios
  ${GREEN}restart${NC}          Reiniciar todos los servicios
  ${GREEN}build${NC}            Construir imágenes desde cero e iniciar servicios
  ${GREEN}rebuild${NC}          Reconstruir imágenes (usa cache) y reiniciar servicios
  ${GREEN}logs${NC} [SERVICIO]  Seguir logs (todos los servicios o un servicio específico)
  ${GREEN}status${NC}           Mostrar estado de servicios y URLs
  ${GREEN}clean${NC}            Eliminar contenedores, volúmenes e imágenes
  ${GREEN}help${NC}             Mostrar esta ayuda

${CYAN}EJEMPLOS:${NC}
  ./run.sh start dev            # Iniciar servicios de desarrollo
  ./run.sh start prd            # Iniciar servicios de producción
  ./run.sh logs backend dev     # Ver logs del backend en dev
  ./run.sh rebuild prd          # Reconstruir servicios de producción
  ./run.sh clean dev            # Limpiar entorno de desarrollo
"
}

# MAIN
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    cmd="$1"
    mode="${2:-dev}"
    case "$cmd" in
        start)    start "$mode" ;;
        stop)     stop "$mode" ;;
        restart)  restart "$mode" ;;
        build)    build "$mode" ;;
        rebuild)  rebuild "$mode" ;;
        logs)     logs "$mode" "$3" ;;
        status)   status "$mode" ;;
        clean)    clean "$mode" ;;
        help|--help|-h) show_help ;;
        *) 
            print_error "Comando desconocido: $cmd"
            echo "Ejecute './run.sh help' para ver los comandos disponibles"
            exit 1
            ;;
    esac
}

main "$@"
