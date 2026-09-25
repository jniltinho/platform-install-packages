package kaltura

// Entry status groups, from the Kaltura 18.20 entryStatus enum
// (alpha/lib/enums/entryStatus.php): -2 ERROR_IMPORTING, -1 ERROR_CONVERTING,
// 0 IMPORT, 1 PRECONVERT, 2 READY, 3 DELETED, 4 PENDING, 5 MODERATE,
// 6 BLOCKED, 7 NO_CONTENT.
const (
	GroupReady      = "ready"
	GroupProcessing = "processing"
	GroupError      = "error"
	GroupOther      = "other"
)

// StatusReady and the processing/error status sets used by the dashboard.
var (
	StatusReady      = []int{2}
	StatusProcessing = []int{0, 1, 4}
	StatusError      = []int{-2, -1}
)

var entryStatusLabels = map[int]string{
	-2: "Erro na importação", -1: "Erro na conversão", 0: "Importando", 1: "Processando",
	2: "Pronto", 3: "Excluído", 4: "Pendente", 5: "Em moderação", 6: "Bloqueado", 7: "Sem conteúdo",
}

// EntryStatusGroup maps an entry status to its UI group.
func EntryStatusGroup(status int) string {
	switch status {
	case 2:
		return GroupReady
	case 0, 1, 4:
		return GroupProcessing
	case -2, -1:
		return GroupError
	default:
		return GroupOther
	}
}

// EntryStatusLabel returns the pt-BR label of an entry status.
func EntryStatusLabel(status int) string {
	if l, ok := entryStatusLabels[status]; ok {
		return l
	}
	return "Desconhecido"
}

var flavorStatusLabels = map[int]string{
	-1: "Erro", 0: "Enfileirado", 1: "Convertendo", 2: "Pronto", 3: "Excluído",
	4: "Não aplicável", 5: "Temporário", 6: "Aguardando", 7: "Importando", 8: "Validando", 9: "Exportando",
}

// FlavorStatusGroup maps a flavor asset status to its UI group.
func FlavorStatusGroup(status int) string {
	switch status {
	case 2:
		return GroupReady
	case 0, 1, 6, 7, 8, 9:
		return GroupProcessing
	case -1:
		return GroupError
	default:
		return GroupOther
	}
}

// FlavorStatusLabel returns the pt-BR label of a flavor asset status.
func FlavorStatusLabel(status int) string {
	if l, ok := flavorStatusLabels[status]; ok {
		return l
	}
	return "Desconhecido"
}
