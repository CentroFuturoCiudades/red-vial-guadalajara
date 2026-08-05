rm(list=ls())
library(tidyverse)
library(srvyr)

### Set the working directory
setwd("C:/Users/cemad/OneDrive - University of Toronto/UofT/Research/Tec_GDL/employment/informal_jobs/ENOE")

# El primero paso para juntar las bases es leer a cada una de forma separada#
viv <- read_csv("enoe_2023_trim1_csv/ENOE_VIVT123.csv", locale = locale(encoding = "Latin1"))
sdem <- read_csv("enoe_2023_trim1_csv/ENOE_SDEMT123.csv", locale = locale(encoding = "Latin1"))
coe1 <- read_csv("enoe_2023_trim1_csv/ENOE_COE1T123.csv", locale = locale(encoding = "Latin1"))
coe2 <- read_csv("enoe_2023_trim1_csv/ENOE_COE2T123.csv", locale = locale(encoding = "Latin1"))
hog <- read_csv("enoe_2023_trim1_csv/ENOE_HOGT123.csv", locale = locale(encoding = "Latin1"))

#dim(sdem)
#head(sdem)


# Una vez leídas las bases, se continúa a juntarlas. 

hog$cd_a
viv_hog <- viv %>% 
  right_join(hog,  by = c("tipo","mes_cal", "cd_a", "ent",
                          "con","v_sel"), suffix = c("", ".hogar"), multiple = "all") %>% 
  right_join(sdem, by = c("tipo","mes_cal", "cd_a", "ent",
                          "con","v_sel" ,
                          "n_hog","h_mud"), suffix = c("", ".sdem"), multiple = "all") %>% 
  left_join(coe1,by = c("tipo","mes_cal", "cd_a", "ent",
                        "con","v_sel" ,
                        "n_hog","h_mud", "n_ren"), suffix = c("", ".coe1"), multiple = "all")  %>% 
  left_join(coe2, by = c("tipo","mes_cal", "cd_a", "ent",
                         "con","v_sel" ,
                         "n_hog","h_mud", "n_ren"), suffix = c("", ".coe2"), multiple = "all")  

#Al haberse hecho el join, se prosigue a verificar que se haya hecho bien. Esto se hace comparado los resultados con aquellos obtenidos por el INEGI. Para esto, se debe aplicar un ambiente de encuesta. 


svv <- as_survey_design(viv_hog, weights = "fac_tri", strata = "est", ids = "upm")

sum(viv_hog$fac_tri.sdem)
## EL numero de habitantes era 126,371,358 en 2019
svv %>% 
  survey_count()


## EL numero de poblacion informal era 31,314,249 en 2019
viv_hog$emp_ppal


svv %>% 
  group_by(emp_ppal) %>% 
  summarise(survey_total(vartype = NULL))


write_csv(viv_hog, "enoe_juntado1t23.csv")



