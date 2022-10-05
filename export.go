package main

import (
	"encoding/json"
	"fmt"
	"os"
	"log"
)

type InputJson struct {
	Ids []string `json:"ids"`
}

func main() {
	var data []byte 
  data, err := os.ReadFile("members.json")
	if err != nil {
		log.Fatal(err)
	}

	var iJson InputJson
	err = json.Unmarshal(data, &iJson)
	if err != nil {
		log.Fatal(err)
	}

  log.Printf("Found %d entries", len(iJson.Ids))

	for i := 0; i < len(iJson.Ids); i++ {
		fmt.Printf("%s,", iJson.Ids[i])
	}
}
