from rag.ingest import ingest_pdf
from rag.retrieve import retrieve_context

ingest_pdf("data/Aditya_Prajapati_Resume.pdf")


print("\n--- CONTEXT ---\n")
print(retrieve_context("What is this document about?"))
